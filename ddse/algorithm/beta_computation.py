"""Helper functions for voltage prediction in state estimation."""

import numpy as np
from dateutil import parser


def check_intervals(timestamps):
    """
    Checks whether the time intervals between timestamps are 15 or 30 minutes only.

    Parameters:
        timestamps: list of ISO 8601 strings

    Returns:
        True if all intervals are 15 or 30 minutes, False otherwise.
    """
    times = [parser.parse(ts) for ts in timestamps]
    for t1, t2 in zip(times, times[1:]):
        delta_minutes = (t2 - t1).total_seconds() / 60
        return delta_minutes


def number_daily_meas(delta):

    return int(24 * 60 / delta)


def beta_pred(volt_known, volt_uknown, daily_meas):
    """Estimates regression coefficients (beta) to predict unknown voltages.

    This function performs linear regression to estimate the voltage of unknown meters
    based on:
      - voltage values of known meters (used as regressors),
      - past values of the same unknown meters (lags of 1, 2, and 7 days).

    It builds a regression dataset by combining:
      - 3 lagged versions of the unknown meter voltages (1-day, 2-day, 7-day),
      - repeated known meter voltages,
    and fits a least squares model for each unknown meter.

    Args:
        volt_known (np.ndarray): Known voltages of shape (K, T), where K is number of known meters.
        volt_uknown (np.ndarray): Unknown voltages of shape (U, T), where U is number of unknown meters.
        daily_meas (int): Number of measurements per day (used to compute time lags).

    Returns:
        np.ndarray: Beta coefficients of shape (3 + K, U), where each column contains
                    the regression weights for one unknown meter.
    """

    # U = number of unknown meters, n_times = number of time points
    U, n_times = np.shape(volt_uknown)
    K = len(volt_known)

    # Repeat known voltages across U unknown meters to match regression shape
    volt_known_repeated = np.tile(volt_known[:, None, :], (1, U, 1))

    # Array to hold past values of unknown voltages (1d, 2d, 7d lags)
    previous_v_data = np.zeros((3, U, n_times))

    # Extend volt_uknown array to the left with NaNs for historical padding
    v_extended = np.zeros(np.shape(volt_uknown) + np.array([0, daily_meas * 7]))
    v_extended[:, : 48 * 7] = np.nan  # Padding 7 days of NaNs
    v_extended[:, 48 * 7 :] = volt_uknown

    # Generate lagged versions of volt_uknown (1, 2, 7 days)
    previous_v_data[0] = np.roll(v_extended, daily_meas, 1)[:, daily_meas * 7 :]
    previous_v_data[1] = np.roll(v_extended, daily_meas * 2, 1)[:, daily_meas * 7 :]
    previous_v_data[2] = np.roll(v_extended, daily_meas * 7, 1)[:, daily_meas * 7 :]

    # Create full regressor matrix: 3 lags + known voltages
    v_data_regr = np.zeros((3 + K, U, n_times))
    v_data_regr[:3] = previous_v_data
    v_data_regr[3:] = volt_known_repeated

    # Placeholder for beta coefficients (regressors × unknown meters)
    beta = np.zeros((3 + K, U))

    for i in range(U):
        # For each unknown meter, extract its regressors and target output
        v_data_reg_meter_i = v_data_regr[:, i, :]
        output_v_data = volt_uknown[i]

        # Remove initial padded period (7 days) for clean training
        v_data_reg_meter_i_noNans = v_data_reg_meter_i[:, daily_meas * 7 :]
        output_v_data_noNans = output_v_data[daily_meas * 7 :]

        # Perform least squares regression: regressors → target
        beta_matr = np.linalg.lstsq(v_data_reg_meter_i_noNans.T, output_v_data_noNans, rcond=None)

        # Store beta coefficients for this unknown meter
        beta[:, i] = beta_matr[0]

    return beta


def v_pred(exc_voltages, actual_volt, beta):
    """Predicts the current voltages for excluded meters using regression coefficients.

    This function performs a linear prediction for each excluded meter using:
      - The voltage values of that meter from previous time steps (1-day, 2-day, 7-day lags),
      - The current voltage values of the known (included) meters,
      - The previously estimated regression coefficients (beta).

    Args:
        exc_voltages (np.ndarray): Array of shape (3, U), containing the lagged voltages
                                   for each of the U excluded meters (1-day, 2-day, 7-day).
        actual_volt (np.ndarray): Array of shape (K,), containing current voltages
                                  of the K known (included) meters.
        beta (np.ndarray): Regression coefficients of shape (3 + K, U), where each column
                           corresponds to the coefficients for one excluded meter.

    Returns:
        np.ndarray: Predicted voltage values for each excluded meter, shape (U,).
    """
    _, U = np.shape(exc_voltages)  # U = number of excluded meters
    K = len(actual_volt)  # K = number of known meters

    v_pred = np.zeros(U)  # Output vector for predicted voltages

    for i in range(U):
        # Create the input feature vector for this excluded meter
        indep = np.zeros(3 + K)
        indep[:3] = exc_voltages[:, i]  # Add lagged voltages (1d, 2d, 7d)
        indep[3:] = actual_volt  # Add current voltages of known meters

        # Compute the linear prediction: dot product with beta coefficients
        v_pred[i] = np.dot(indep, beta[:, i])

    return v_pred
