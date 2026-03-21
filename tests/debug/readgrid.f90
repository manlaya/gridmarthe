program test_readgrid

  use MODGRIDMARTHE, only: read_grid, SCAN_DIM

  implicit none

  character(len=132) :: filename, variable, title
  real(kind=8), dimension(:,:), allocatable :: array
  real(kind=4), dimension(:,:), allocatable :: xc, yc, dx, dy
  real(kind=4), dimension(:)  , allocatable :: timesteps
  integer     , dimension(:)  , allocatable :: itimes
  integer :: KNBSTEP, KDIMEN(99,3), KNU_ZOOMX, KNBTOT, i

  ! Get the filename for the grid file
  ! call get_command_argument(1, filename)
  ! call get_command_argument(2, variable)

  ! filename = '../data/grid_wrong_attrs.hsubs'
  filename = '../data/test_multilay_nest_no_metadata.permh'
  ! filename = '../data/Somme_V3_Surfex.permh'
  ! filename = '../data/craie_npc_gig.permh'
  variable = ''

  print *, 'Testing read_grid with file: ', trim(filename), ' and variable: ', trim(variable)
  call SCAN_DIM(filename, variable, KDIMEN, KNBSTEP)
  KNBTOT = product(KDIMEN(1, :)) + product(KDIMEN(2, :))

  print *, 'KNBSTEP:', KNBSTEP
  print *, 'KDIMEN:'
  do i=1, 2
    print *, KDIMEN(i, 1:3)
  end do
  print *, 'KNU_ZOOMX:', KNU_ZOOMX
  print *, 'KNBTOT:', KNBTOT

  ! call read_grid( &
  !   filename, &
  !   variable, &
  !   KNBSTEP, KNBTOT, KNU_ZOOMX, array, timesteps, &
  !   itimes, xc, yc, dx, dy, title &
  ! )

  ! contains

    ! subroutine nc_check(status)
    !     use netcdf
    !     implicit none
    !     integer, intent(in) :: status
    !     if (status /= nf90_noerr) then
    !         print *, trim(nf90_strerror(status))
    !         stop "Stopped"
    !     end if
    ! end subroutine nc_check

end program test_readgrid
