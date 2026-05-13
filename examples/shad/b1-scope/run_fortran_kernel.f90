! SPDX-License-Identifier: Apache-2.0
!
! run_fortran_kernel.f90 -- push the B0 Slot S1 golden vector through the
! lege-artis/fourier Fortran reference kernel and print the output.
!
! Mirrors examples/shad/b1-scope/run_cpp_kernel.cpp at line-level intent.
! The Python orchestrator render_components.py subprocesses this binary
! with the --csv flag and parses one row per output bin.
!
! Build (from repo root):
!   cd backends/fortran && make                    # builds dft_kernel.o + .mod
!   python tools/json_to_fortran_data.py           # creates build/golden/*.dat
!   gfortran -O0 -g -std=f2018 -fimplicit-none -ffp-contract=off \
!     -Ibackends/fortran/build \
!     examples/shad/b1-scope/run_fortran_kernel.f90 \
!     backends/fortran/build/dft_kernel.o \
!     -o examples/shad/b1-scope/run_fortran_kernel
!
! Run:
!   ./examples/shad/b1-scope/run_fortran_kernel \
!     backends/fortran/build/golden/dft_n_64.dat cos1_plus_cos2 [--csv]
!
! Output (human mode): the same listing shape as the C++ CLI -- N, case,
! max-err, agreement, head of input + head of output.
! Output (--csv mode):  one CSV row per bin: bin,re,im,mag.
!
! ASCII-only source per KB-039 / WORKING-SPEC-v0.3-EN.md section 4.1.

program run_fortran_kernel
  use lege_artis_fourier_dft, only: dft, dp
  implicit none

  character(len=256) :: dat_path, case_arg, arg
  character(len=64)  :: case_name, target_case
  logical            :: csv_mode
  integer            :: i, argc, nlen, num_cases, unit_num, ios
  integer            :: case_idx, k
  integer            :: dummy_n
  real(dp)           :: re_val, im_val, max_err, this_err, gate
  complex(dp), allocatable :: x_in(:), x_out_oracle(:), x_kernel(:)
  logical            :: found

  ! ---- argument parsing -------------------------------------------------
  argc = command_argument_count()
  if (argc < 1) then
    write(*, '(a)') 'usage: run_fortran_kernel <dat_path> [<case_name>=cos1_plus_cos2] [--csv]'
    stop 2
  end if
  call get_command_argument(1, dat_path)

  target_case = 'cos1_plus_cos2'
  csv_mode    = .false.
  do i = 2, argc
    call get_command_argument(i, arg)
    if (trim(arg) == '--csv') then
      csv_mode = .true.
    else
      target_case = trim(arg)
    end if
  end do

  ! ---- open the .dat fixture --------------------------------------------
  open(newunit=unit_num, file=trim(dat_path), status='old', action='read', &
       form='formatted', iostat=ios)
  if (ios /= 0) then
    write(*, '(3a)') 'FATAL: cannot open [', trim(dat_path), ']'
    write(*, '(a)')  '       Run: python tools/json_to_fortran_data.py'
    stop 2
  end if

  read(unit_num, *) nlen, num_cases
  allocate(x_in(nlen), x_out_oracle(nlen))

  ! ---- scan for the requested case --------------------------------------
  found = .false.
  do case_idx = 1, num_cases
    read(unit_num, '(a64)') case_name
    if (trim(case_name) == trim(target_case)) then
      found = .true.
      ! read input
      do k = 1, nlen
        read(unit_num, *) re_val, im_val
        x_in(k) = cmplx(re_val, im_val, kind=dp)
      end do
      ! read oracle output
      do k = 1, nlen
        read(unit_num, *) re_val, im_val
        x_out_oracle(k) = cmplx(re_val, im_val, kind=dp)
      end do
      exit
    else
      ! skip this case (2*N data lines)
      do k = 1, 2 * nlen
        read(unit_num, *)
      end do
    end if
  end do
  close(unit_num)

  if (.not. found) then
    write(*, '(3a)') 'FATAL: case [', trim(target_case), '] not found in fixture'
    stop 2
  end if

  ! ---- *** push data into the lege-artis/fourier Fortran kernel *** -----
  x_kernel = dft(x_in)

  ! ---- compute max abs error vs oracle ----------------------------------
  max_err = 0.0_dp
  do k = 1, nlen
    this_err = abs(x_kernel(k) - x_out_oracle(k))
    if (this_err > max_err) max_err = this_err
  end do

  ! ---- output -----------------------------------------------------------
  if (csv_mode) then
    write(*, '(a)') 'bin,re,im,mag'
    do k = 1, nlen
      write(*, '(i0,",",es24.17,",",es24.17,",",es24.17)') &
        k - 1, real(x_kernel(k), dp), aimag(x_kernel(k)), abs(x_kernel(k))
    end do
  else
    ! Pragmatic gate matches C++ CLI: 1e-12 for N=64 direct O(N^2) evaluation.
    gate = 1.0e-12_dp
    write(*, '(a)') '--- lege-artis/fourier Fortran reference kernel ---'
    write(*, '(a,i0)')        'N           = ', nlen
    write(*, '(2a)')          'case        = ', trim(target_case)
    write(*, '(a,es10.3,a,i0,a)') 'max abs err = ', max_err, &
                                    '   (engineering gate 1e-12 for N=', nlen, ')'
    if (max_err < gate) then
      write(*, '(a)') 'agreement   = PASS'
    else
      write(*, '(a)') 'agreement   = FAIL'
    end if
    write(*, '(a)') ''
    write(*, '(a)') 'first 8 inputs (real part only - input is real-valued):'
    do k = 1, min(8, nlen)
      write(*, '(a,i2,a,sp,f15.10)') '  x[', k - 1, '] = ', real(x_in(k), dp)
    end do
    write(*, '(a)') ''
    write(*, '(a)') 'first 8 outputs:'
    do k = 1, min(8, nlen)
      write(*, '(a,i2,a,sp,f9.4,1x,f9.4,a,a,i2,a,f9.4)') &
        '  X[', k - 1, '] = ', real(x_kernel(k), dp), aimag(x_kernel(k)), 'j   ', &
        '|X[', k - 1, ']| = ', abs(x_kernel(k))
    end do
  end if

  deallocate(x_in, x_out_oracle, x_kernel)

end program run_fortran_kernel
