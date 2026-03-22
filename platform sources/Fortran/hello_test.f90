program HelloTest
    !! Fortran Hello World Test
    !!
    !! A simple test program that demonstrates Fortran functionality
    !! including string operations, arithmetic, and assertions.

    implicit none

    character(len=50) :: greeting
    character(len=50) :: expected
    character(len=100) :: extended_greeting
    integer :: a, b, sum_result
    integer :: i, array_sum
    integer :: numbers(5)
    logical :: test_passed

    print *, "Starting Fortran Hello World Test..."

    ! Test 1: Basic string output
    greeting = "Hello, World!"
    print *, trim(greeting)
    call assert_true(len_trim(greeting) == 13, "Greeting length test")

    ! Test 2: String comparison
    expected = "Hello, World!"
    call assert_true(trim(greeting) == trim(expected), "String comparison test")

    ! Test 3: Basic arithmetic
    a = 5
    b = 3
    sum_result = a + b
    call assert_equal(sum_result, 8, "Arithmetic test")
    print *, a, " + ", b, " = ", sum_result

    ! Test 4: Multiple assertions
    call assert_true(a > b, "Comparison test a > b")
    call assert_true(b < a, "Comparison test b < a")
    call assert_true(sum_result > 0, "Comparison test sum > 0")

    ! Test 5: String manipulation
    extended_greeting = trim(greeting) // " (From Fortran)"
    print *, trim(extended_greeting)
    call assert_true(index(extended_greeting, "Fortran") > 0, "String contains test")

    ! Test 6: Array operations and summation
    numbers = [1, 2, 3, 4, 5]
    array_sum = sum(numbers)
    call assert_equal(array_sum, 15, "Array sum test")
    print *, "Sum of [1, 2, 3, 4, 5] = ", array_sum

    ! Test 7: Iteration and array operations
    print *, "Array elements: "
    do i = 1, size(numbers)
        print *, "  numbers(", i, ") = ", numbers(i)
    end do

    ! Test 8: Array filtering (count even numbers)
    call assert_equal(count_even(numbers), 2, "Count even numbers test")

    ! Test 9: Maximum and minimum
    call assert_equal(maxval(numbers), 5, "Maxval test")
    call assert_equal(minval(numbers), 1, "Minval test")

    ! Test 10: Floating point operations
    call test_floating_point()

    print *, "All Fortran tests passed successfully!"

contains

    subroutine assert_true(condition, message)
        logical, intent(in) :: condition
        character(len=*), intent(in) :: message

        if (.not. condition) then
            print *, "ASSERTION FAILED: ", trim(message)
            stop 1
        else
            print *, "PASSED: ", trim(message)
        end if
    end subroutine assert_true

    subroutine assert_equal(actual, expected, message)
        integer, intent(in) :: actual, expected
        character(len=*), intent(in) :: message

        if (actual /= expected) then
            print *, "ASSERTION FAILED: ", trim(message)
            print *, "  Expected: ", expected
            print *, "  Actual: ", actual
            stop 1
        else
            print *, "PASSED: ", trim(message)
        end if
    end subroutine assert_equal

    function count_even(arr) result(count)
        integer, intent(in) :: arr(:)
        integer :: count
        integer :: i

        count = 0
        do i = 1, size(arr)
            if (mod(arr(i), 2) == 0) then
                count = count + 1
            end if
        end do
    end function count_even

    subroutine test_floating_point()
        real :: x, y, result
        character(len=50) :: message

        x = 3.5
        y = 2.5
        result = x + y

        if (abs(result - 6.0) < 1e-6) then
            print *, "PASSED: Floating point test"
        else
            print *, "ASSERTION FAILED: Floating point test"
            stop 1
        end if
    end subroutine test_floating_point

end program HelloTest
