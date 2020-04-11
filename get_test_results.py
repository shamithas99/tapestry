### Get the results for a given test. Implemented in function get_test_results() ###

# This is where the actual get_test_results() is present
import app
import config

# Import the dictionary of matrix labels to the actual numpy matrices
#
# This dictionary is **auto-generated** by looking at all the variables named
# optimized_M_* in matrices.py and matrices1.py
from matrices import MDict as MLabelToMatrixDict

# Dictionary of matrix size to the label of the matrix which will be used. 
# This dictionary should be modified by hand.
#
# Matrix Sizes are strings such as "46x96", "46x192"
#
# Matrix labels are the actual variable names used for the matrices in
# matrices.py and matrices1.py
#
# Warning: during deployment, once a matrix size is added, it should never be
# removed. Once a matrix label is added, it should never be removed from the
# code. 
MSizeToLabelDict = {
    "16x40":    "optimized_M_16_40_ncbs",
    "24x60":    "optimized_M_3",
    "46x96":    "optimized_M_46_96_1",
    "46x192":   "optimized_M_46_192_1",
    }

# Returns a copy of size -> label dictionary
def get_matrix_sizes_and_labels():
  return dict(MSizeToLabelDict)

# Returns the currently used matrix label for a given size
def get_current_matrix_label_for_size(matrix_size):
  if not matrix_size in MSizeToLabelDict:
    raise KeyError('Invalid matrix size: "%s". Correct matrix sizes are: "%s"' %
        (matrix_size, '", "'.join(MSizeToLabelDict.keys())))

  return MSizeToLabelDict[matrix_size]

# Returns the matrix (which is a numpy array of shape (t, n)) corresponding to
# the given label
def get_matrix_for_label(matrix_label):
  if not matrix_label in MLabelToMatrixDict:
    raise KeyError('Invalid matrix label: "%s". Correct matrix labels are: "%s"' %
        (matrix_label, '", "'.join(MLabelToMatrixDict.keys())))
  return MLabelToMatrixDict[matrix_label]

# Get the results for a test
#
# Input: Matrix label on which the test was performed. Such as
# "optimized_M_46_96_1"
#
# Input: Cycle time vector. Numpy array of size 't', which is the number of
# tests or equivalently the number of rows in the matrix
def get_test_results(matrix_label, cycle_times):
  M = get_matrix_for_label(matrix_label)

  sure_list, unsure_list, neg_list, x = app.get_test_results(M, cycle_times)

  result_string = get_result_string_from_lists(sure_list, unsure_list, neg_list, x)
  return result_string

# Composes the result string from the list of surely positives, possibly
# positives, negatives and the x values
def get_result_string_from_lists(sure_list, unsure_list, neg_list, x):
  if not sure_list and not unsure_list:
    s0 = "No Positive Samples\n"
    s3 = "All samples are negative\n"

    s1 = ""
    s2 = ""
  else:
    s0 = ""
    if sure_list:
      s1  = "Surely Positive Samples: %s \n" % \
          ", ".join([str(item) for item in sure_list])
    else:
      s1  = "No Surely Positive Samples"

    if unsure_list:
      s2  = "Possibly Positive Samples: %s \n" % \
          ", ".join([str(item) for item in unsure_list])
    else:
      s2  = ""

    if not neg_list:
      s3 = "No surely negative samples detected\n"
    else:
      s3 = "Remaining samples are negative\n"

  x_str = ""
  if config.app_algo != 'COMP':
    x_str = "Detected viral loads: %s" % \
            ", ".join([str(item) for item in x])
  result_string = s0 + s1 + s2 + s3 + x_str

  return result_string

# Code to run at deployment time. Checks for errors such as invalid matrix
# labels or sizes. If this raises an exception, then deployment should not
# happen and a notification must be sent.
def at_deployment():
  sanity_check_for_matrices()





###########      Internal Code for testing      ##############

def test_get_result_string_from_lists():
  sure_list = [2, 17, 29]
  unsure_list = [25, 78]
  neg_list = list(range(1, 97))
  for item in (sure_list + unsure_list):
    neg_list.remove(item)
  x = np.random.rand(96)
  res = get_result_string_from_lists(sure_list, unsure_list, neg_list, x)
  print(res)


# Go through all the labels in MSizeToLabelDict and determine if the corresponding
# matrices are present MLabelToMatrixDict. Checks if the sizes match up.
def sanity_check_for_matrices():
  print('Checking if matrix sizes correspond to an actual label...\n')
  error = False
  for msize in MSizeToLabelDict:
    t, n = [int(item) for item in msize.split("x")]
    mlabel = MSizeToLabelDict[msize]
    if mlabel in MLabelToMatrixDict:
      print(msize, mlabel, 'label exists')
      M = MLabelToMatrixDict[mlabel]
      if t == M.shape[0] and  n == M.shape[1]:
        print(msize, mlabel, 'Sizes match')
      else:
        print('********   Error: ', msize, mlabel, 'Sizes don\'t match:',
            M.shape, "   ********")
        error = True
    else:
      print(msize, mlabel, 'label does not exists')
      error = True
  if error:
    print("\nGot Error :(\n")
    raise ValueError("Some error in matrix setup")
  else:
    print("\nAll OK\n")
  
def api_sanity_checks():
  error = False
  print('\nSome API checks...\n')
  print('Label for valid size 46x96', get_current_matrix_label_for_size("46x96"))
  try:
    print(get_current_matrix_label_for_size("fslkj"))
    print('Did not get expected error while calling with invalid matrix size')
    error = True
  except KeyError as e:
    print('Got expected error while calling with invalid matrix size:', str(e))

  
  print('Shape of the valid matrix optimized_M_16_40_ncbs', get_matrix_for_label("optimized_M_16_40_ncbs").shape)
  try:
    invalid_label = "ojlkj"
    print('shape of the invalid matrix ', invalid_label,
        get_matrix_for_label(invalid_label).shape)
    print('Did not get expected error while calling with invalid matrix size')
    error = True
  except KeyError as e:
    print('Got expected error while calling with invalid matrix label:', str(e))
  if error:
    print("\nGot Error :(\n")
    raise ValueError("Some error in matrix setup")
  else:
    print("\nAll OK\n")

if __name__ == '__main__':
  import numpy as np

  sanity_check_for_matrices()
  api_sanity_checks()
  test_get_result_string_from_lists()
  # Now test get_test_results()
  from experimental_data_manager import read_harvard_data_cts
  cts = read_harvard_data_cts()
  res = get_test_results("optimized_M_3", cts)
  print(res)

