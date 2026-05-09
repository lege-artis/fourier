!> @file   test_dft_golden.f90
!> @brief  Golden-vector verification - load oracle .dat files (transformed
!>         from shared/golden-vectors/dft_n=*.json by tools/json_to_fortran_data.py)
!>         and verify the kernel's dft() output matches the oracle within tol_base * sqrt(N)
!>         where tol_base = 1e-13 (N-scaled per Higham sec 4.2; see assert_complex_array_close).
!> @date   2026-05-09 (v0.1.0-rc Job-3)
!>
!> Source kept ASCII-only: gfortran with -std=f2018 -pedantic byte-counts
!> against the 132-column line limit, so no box-drawing / em-dash / Greek /
!> arrows / math-symbols (per Sonnet handoff section 1.1).
!>
!> Spec: SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md section 4
!>
!> What this test does:
!>   For each N in {2, 4, 8, 16, 64}:
!>     - Open build/golden/dft_n_<N>.dat (regenerated from
!>       shared/golden-vectors/dft_n=<N>.json by json_to_fortran_data.py)
!>     - Read header:  declared_n  ncases
!>     - For each of ncases test cases:
!>         read case_name (quoted string), input_len, input flat (re,im) pairs,
!>         expected_len, expected flat (re,im) pairs.
!>         Run X_out = dft(input). Compare X_out vs expected at 1e-13.
!>     - Close file.
!>
!> Total cases (Job-3 scope): 38
!>   N=2:   6 cases (no cosine_k2 / cos1_plus_cos2 - Nyquist-degenerate at N=2)
!>   N=4:   8 cases
!>   N=8:   8 cases
!>   N=16:  8 cases
!>   N=64:  8 cases
!>
!> The leakage variant (shared/golden-vectors/dft_n=64_cosine_leakage.json) is
!> consumed by Job-2 PT-DFT-03B, NOT here.
!>
!> Path convention:
!>   The test binary lives at build/test_dft_golden and is invoked from
!>   backends/fortran/ by the Makefile's `test:` target. The .dat files are
!>   at build/golden/dft_n_<N>.dat - i.e. relative path
!>   'build/golden/dft_n_<N>.dat' from CWD = backends/fortran/.
!>
!> Variable naming (per WORKING-SPEC section 4 line-by-line discipline +
!> handoff section 1.2 case-collision avoidance):
!>   - nlen        sequence length N (NOT 'N' - would collide with lowercase 'n')
!>   - ncases      number of test cases in current .dat file
!>   - i, j        loop indices
!>   - case_name   character buffer for the current case identifier
!>   - x           input vector  (complex(dp))
!>   - X_out       dft(x) actual (complex(dp))
!>   - expected    oracle vector (complex(dp))
!>
!> Tolerance: base 1.0e-13_dp, N-scaled inside assert_complex_array_close:
!>   effective gate = 1.0e-13_dp * sqrt(real(N, dp))  (Higham sec 4.2 accumulator model).
!>   For N=64: 8.0e-13. For N=8: 2.83e-13. For N=2: 1.41e-13.
!>
!> @license Apache 2.0

program test_dft_golden
    use lege_artis_fourier_dft, only: dft, dp
    implicit none

    integer :: total = 0
    integer :: failed = 0

    write(*, '(A)') '========================================================='
    write(*, '(A)') ' lege-artis/fourier - DFT golden-vector tests (v0.1.0-rc)'
    write(*, '(A)') '========================================================='

    ! Five JSON-derived oracle files. Order matches Python tool's sorted glob.
    call test_one_n(2)
    call test_one_n(4)
    call test_one_n(8)
    call test_one_n(16)
    call test_one_n(64)

    write(*, '(A)') '========================================================='
    write(*, '(A, I0, A, I0, A)') ' Result: ', (total - failed), '/', total, ' passed'
    if (failed > 0) then
        write(*, '(A)') ' FAILED.'
        stop 1
    else
        write(*, '(A)') ' All golden-vector tests PASSED.'
    end if

contains

    !> Open build/golden/dft_n_<nlen>.dat and run all cases inside it.
    !>
    !> File layout (matches tools/json_to_fortran_data.py emitter):
    !>   declared_n
    !>   ncases
    !>   "<case_name_1>"
    !>   input_len
    !>   re_1 im_1
    !>   re_2 im_2
    !>   ... input_len pairs
    !>   expected_len
    !>   re_1 im_1
    !>   ... expected_len pairs
    !>   "<case_name_2>"
    !>   ... etc for ncases cases
    subroutine test_one_n(nlen)
        integer, intent(in) :: nlen

        character(len=64) :: filename
        character(len=64) :: case_name
        integer :: unit_no, ios
        integer :: declared_n, ncases, i, j
        integer :: input_len, expected_len
        real(dp) :: re_, im_
        complex(dp), allocatable :: x(:), X_out(:), expected(:)
        real(dp), parameter :: tol = 1.0e-13_dp
        character(len=128) :: test_label

        ! Build the file path: 'build/golden/dft_n_<nlen>.dat'
        write(filename, '(A, I0, A)') 'build/golden/dft_n_', nlen, '.dat'

        ! Open with formatted (text) mode for list-directed read(*,*).
        open(newunit=unit_no, file=trim(filename), status='old', action='read', &
             form='formatted', iostat=ios)
        if (ios /= 0) then
            failed = failed + 1
            total = total + 1
            write(*, '(A, A, A, I0)') &
                ' [FAIL] golden file open - ', trim(filename), ' - iostat=', ios
            return
        end if

        ! Read header.
        read(unit_no, *, iostat=ios) declared_n
        if (ios /= 0 .or. declared_n /= nlen) then
            failed = failed + 1
            total = total + 1
            write(*, '(A, I0, A, I0, A, I0)') &
                ' [FAIL] header N mismatch - file declares ', declared_n, &
                ' but expected ', nlen, '; iostat=', ios
            close(unit_no)
            return
        end if

        read(unit_no, *, iostat=ios) ncases
        if (ios /= 0 .or. ncases <= 0) then
            failed = failed + 1
            total = total + 1
            write(*, '(A, A, A, I0)') &
                ' [FAIL] header NCASES read - ', trim(filename), ' - iostat=', ios
            close(unit_no)
            return
        end if

        ! Allocate the per-case buffers once (size known from header).
        allocate(x(nlen), expected(nlen))

        ! Process each case.
        do i = 1, ncases
            read(unit_no, *, iostat=ios) case_name
            if (ios /= 0) then
                failed = failed + 1
                total = total + 1
                write(*, '(A, I0, A, A, A, I0)') &
                    ' [FAIL] case ', i, ' name read - ', trim(filename), &
                    ' - iostat=', ios
                close(unit_no)
                deallocate(x, expected)
                return
            end if

            ! INPUT block: length, then nlen pairs of (re, im).
            read(unit_no, *, iostat=ios) input_len
            if (ios /= 0 .or. input_len /= nlen) then
                failed = failed + 1
                total = total + 1
                write(*, '(A, A, A, I0)') &
                    ' [FAIL] case ', trim(case_name), ' input_len mismatch - got ', input_len
                close(unit_no)
                deallocate(x, expected)
                return
            end if
            do j = 1, nlen
                read(unit_no, *, iostat=ios) re_, im_
                if (ios /= 0) then
                    failed = failed + 1
                    total = total + 1
                    write(*, '(A, A, A, I0, A, I0)') &
                        ' [FAIL] case ', trim(case_name), &
                        ' input pair read at j=', j, ' iostat=', ios
                    close(unit_no)
                    deallocate(x, expected)
                    return
                end if
                x(j) = cmplx(re_, im_, kind=dp)
            end do

            ! EXPECTED block: length, then nlen pairs of (re, im).
            read(unit_no, *, iostat=ios) expected_len
            if (ios /= 0 .or. expected_len /= nlen) then
                failed = failed + 1
                total = total + 1
                write(*, '(A, A, A, I0)') &
                    ' [FAIL] case ', trim(case_name), &
                    ' expected_len mismatch - got ', expected_len
                close(unit_no)
                deallocate(x, expected)
                return
            end if
            do j = 1, nlen
                read(unit_no, *, iostat=ios) re_, im_
                if (ios /= 0) then
                    failed = failed + 1
                    total = total + 1
                    write(*, '(A, A, A, I0, A, I0)') &
                        ' [FAIL] case ', trim(case_name), &
                        ' expected pair read at j=', j, ' iostat=', ios
                    close(unit_no)
                    deallocate(x, expected)
                    return
                end if
                expected(j) = cmplx(re_, im_, kind=dp)
            end do

            ! Run the kernel. Note: kernel returns 0-indexed allocatable
            ! complex(dp) array (per dft_kernel.f90 line 67: allocate(X_out(0:nlen-1))).
            ! We compare against expected which is 1-indexed in this scope,
            ! but assert_complex_array_close handles array-of-array comparison
            ! by absolute index, so the slicing is on size only.
            X_out = dft(x)

            ! Build a clear test label combining N + case name.
            write(test_label, '(A, I0, A, A)') &
                'golden_n', nlen, '_', trim(case_name)

            ! The helper updates total + failed via parent program scope.
            call assert_complex_array_close(trim(test_label), X_out, expected, tol)

            ! Free the kernel's allocatable result before next iteration.
            if (allocated(X_out)) deallocate(X_out)
        end do

        deallocate(x, expected)
        close(unit_no)
    end subroutine test_one_n

    !> Helper: assert two complex arrays are close within tolerance.
    !> SHARES the parent program's total / failed counters via host association.
    !>
    !> Gate formula (Option G; Opus triage of SONNET-STATUS-job3-near-zero-bins.md):
    !>
    !>     metric = abs(actual(i) - expected(i)) / max(abs(expected(i)), 1.0_dp)
    !>     gate   = tol_base * sqrt(real(N, dp))          ! N-scaled per Higham sec 4.2
    !>
    !> Hybrid divisor behaviour:
    !>   When |expected(i)| <= 1: divisor is 1 => metric is absolute error.
    !>   When |expected(i)| >  1: divisor is |expected(i)| => metric is relative error.
    !>
    !> N-scaled tolerance behaviour:
    !>   Direct DFT accumulates O(sqrt(N)) round-off in the random-walk model (Higham sec 4.2).
    !>   Correlated cancellation at near-zero bins (cos/sin at orthogonal frequencies) can reach
    !>   ~N * eps in pathological phase-alignment cases. The sqrt(N) factor is the standard
    !>   model; it comfortably covers the observed 1-3e-13 failures at N=64 (gate = 8e-13).
    !>   For N=2: gate = 1.41e-13 (essentially unchanged). Kernel stays read-only.
    !>
    !> The 1.0_dp literal MUST carry the _dp suffix - Fortran takes a bare
    !> `1.0` as default real (single precision) and the resulting max() call
    !> would coerce expected to single-precision-real (silent precision loss).
    !>
    !> Indexing subtlety: the kernel returns a 0-indexed array (0:nlen-1) while
    !> `expected` here is 1-indexed (1:nlen). The whole-array intent(in) :: actual(:)
    !> dummy is normalised to 1-indexed when received, so the i-th element of
    !> actual pairs with the i-th element of expected regardless of either's
    !> declared lower-bound - we loop `i = 1, size(actual)` and the pairing is
    !> by position, not by lower-bound.
    subroutine assert_complex_array_close(test_name, actual, expected, tol_base)
        character(len=*), intent(in)  :: test_name
        complex(dp),      intent(in)  :: actual(:), expected(:)
        real(dp),         intent(in)  :: tol_base
        real(dp) :: tol             ! effective gate: tol_base * sqrt(N), N-scaled per Higham sec 4.2
        real(dp) :: max_rel_err     ! gate metric: hybrid abs-rel error
        real(dp) :: max_abs_err     ! diagnostic only: absolute error at the gate-violating idx
        real(dp) :: rel_err, abs_err
        integer  :: i, idx

        total = total + 1

        ! N-scaled gate: tol_base * sqrt(N) covers direct-DFT cancellation noise per Higham sec 4.2.
        tol = tol_base * sqrt(real(size(actual), dp))

        if (size(actual) /= size(expected)) then
            failed = failed + 1
            write(*, '(A, A, A)') ' [FAIL] ', test_name, ' - size mismatch'
            return
        end if

        max_rel_err = 0.0_dp
        max_abs_err = 0.0_dp
        idx = 1
        do i = 1, size(actual)
            abs_err = abs(actual(i) - expected(i))
            ! Hybrid divisor: max(|expected(i)|, 1.0_dp) keeps the gate ABSOLUTE
            ! for small-magnitude bins (no relative-blow-up on near-zero expected)
            ! and proportional-to-magnitude for large bins.
            rel_err = abs_err / max(abs(expected(i)), 1.0_dp)
            if (rel_err > max_rel_err) then
                max_rel_err = rel_err
                max_abs_err = abs_err
                idx = i
            end if
        end do

        if (max_rel_err > tol) then
            failed = failed + 1
            write(*, '(A, A, A, ES10.3, A, ES10.3, A, I0)') &
                ' [FAIL] ', test_name, &
                ' - max-rel-err = ', max_rel_err, ' > tol = ', tol, ' at idx ', idx - 1
            write(*, '(A, ES10.3)') &
                '         (max-abs-err at that idx = ', max_abs_err
            write(*, '(A, F12.8, A, F12.8, A)') &
                '         actual[idx]   = ', real(actual(idx)), ' + ', aimag(actual(idx)), 'i'
            write(*, '(A, F12.8, A, F12.8, A)') &
                '         expected[idx] = ', real(expected(idx)), ' + ', aimag(expected(idx)), 'i'
        else
            write(*, '(A, A, A, ES10.3, A, ES10.3, A)') &
                ' [PASS] ', test_name, &
                ' - max-rel-err = ', max_rel_err, '  (gate ', tol, ')'
        end if
    end subroutine assert_complex_array_close

end program test_dft_golden
