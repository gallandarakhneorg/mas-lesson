set terminal pdfcairo enhanced color crop size 4in,4in

datafile = exists("ARGC") && ARGC >= 1 ? ARG1 : "staff-per-campus.csv"

radius      = 1.0          # pie radius
labelRadius = 0.68         # radial position of the labels (inside the slices)
DEG2RAD     = pi / 180.0

# Colour palette, cycled if the file contains more campuses than colours.
array COLORS[8]
COLORS[1] = 0x4e79a7
COLORS[2] = 0xf28e2b
COLORS[3] = 0xe15759

# ---------------------------------------------------------------------------
# Input file and total number of persons
# ---------------------------------------------------------------------------
set datafile separator ","        # use ";" here for semicolon-separated files
stats datafile using 2 nooutput
total = STATS_sum

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

unset key
unset tics
unset border
set size ratio -1
set lmargin at screen 0
set rmargin at screen 1
set tmargin at screen 1
set bmargin at screen 0
set xrange [-1:1]
set yrange [-1:1]

# ---------------------------------------------------------------------------
# Pie chart
#   - element 1: the wedges. For each record, c1 accumulates the number of
#     persons; begin/end angles are the cumulative fractions of 360 degrees.
#     A pie slice is drawn from (0,0) because x and y are forced to 0.
#     Column 6 gives the fill colour (lc rgb variable).
#   - element 2: the labels, placed at the mid-angle of each slice.
#     c2 re-accumulates independently (each element reads the file again).
#     Label text = campus name (column 1) + percentage (column 3).
#     If column 3 already contains a "%" sign, replace the sprintf format
#     with sprintf("%s %s", strcol(1), strcol(3)).
# ---------------------------------------------------------------------------
c1 = 0
c2 = 0
plot \
    datafile using \
        (c1 = c1 + $2, 0):(0):(radius):((c1 - $2) * 360.0 / total):(c1 * 360.0 / total):(COLORS[int($0) % 8 + 1]) \
        with circles lc rgb variable fs solid 1.0 border lc rgb "white", \
    datafile using \
        (c2 = c2 + $2, mid = (c2 - $2 / 2.0) * 360.0 / total, labelRadius * cos(mid * DEG2RAD)) \
        :(labelRadius * sin(mid * DEG2RAD)) \
        :(sprintf("%s %g%%", strcol(1), $3)) \
        with labels tc rgb "white" font ",18"

