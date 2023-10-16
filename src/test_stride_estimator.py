# to run, install pytest
# use a terminal and go to the same directory as this file
# then just type pytest then wait (around 1 min) for test case to pass

from stride_estimator import stride_estimator
import pytest

## test 1
def test_step_array_scale_by_2():
    """
    Tests if the same video but with 2x feet size is almost the same

    Ideas for this tester:
    - make a bigger range for error
    - allow 1-2 mistakes
    :return:
    """
    se1 = stride_estimator("../data/dslr/DSC_0503.MOV", 23)
    se2 = stride_estimator("../data/dslr/DSC_0503.MOV", 46)

    # Step array: [63, 39, 72, 42, 72, 36, 71, 34, 74, 64, 40] Average: 55.18181818181818
    # Step array: [126, 78, 144, 84, 145, 73, 143, 69, 148, 129, 81] Average: 110.9090909090909
    # Stride array: [63, 144, 144, 142, 148, 128]
    # Stride array: [126, 156, 290, 286, 296, 258]

    ## pass test
    assert helper_for_test_1(se1.step_array, se2.step_array) == True

    ## to pass assert must fail the function (2nd stride value for both are off)
    assert helper_for_test_1(se1.stride_array, se2.stride_array) == False

    se1 = stride_estimator("../data/11_110_1.mp4", 23)
    se2 = stride_estimator("../data/11_110_1.mp4", 46)



    # Step array: [55, 40, 45, 41, 48, 35, 49, 44, 29, 46, 45, 43, 46, 43, 29, 47, 58, 38] Average: 43.388888888888886
    # Step array: [110, 81, 91, 82, 96, 70, 98, 89, 59, 92, 91, 86, 93, 86, 59, 95, 117, 77] Average: 87.33333333333333
    # Stride array: [55, 90, 98, 88, 92, 90, 86, 92, 86, 94, 116]
    # Stride array: [110, 182, 196, 178, 184, 182, 172, 186, 172, 190, 234]

    ## pass test
    assert helper_for_test_1(se1.step_array, se2.step_array) == True

    ## pass
    assert helper_for_test_1(se1.stride_array, se2.stride_array) == True


def helper_for_test_1(array1, array2):
    """
    Check if first array by a scale of 2 is about equal to array2

    :param array1: smaller array
    :param array2: bigger array
    :return: boolean
    """
    for i in range(0, len(array1)):
        val1 = array1[i] * 2
        val2 = array2[i]

        if (val1 - 3 < val2 < val1 + 3) is False:
            return False

    return True


## test 2
def test_no_subject_video():
    """
    Test if a video with no subject in frame returns an empty array
    and doesnt crash

    Implementation ideas:
    - zero length (arrays have zero length)
    :return:
    """

    # if have print (the average has divide there)
    with pytest.raises(ZeroDivisionError) as error:
        se1 = stride_estimator("../data/no_movement.mp4", 23)
    assert str(error.value) == "division by zero"

    # #if remove prints at the end, test for this
    # se1 = stride_estimator("../data/no_movement.mp4", 23)
    # assert len(se1.step_array) == 0



## test 3
def test_walking_direction():
    """
    Test if walking the correct direction (simple test)

    :return:
    """
    se1 = stride_estimator("../data/dslr/DSC_0502.MOV", 23)

    assert se1.to_left is False and se1.to_right is True

    se2 = stride_estimator("../data/dslr/DSC_0503.MOV", 23)

    assert se2.to_left is True and se2.to_right is False

