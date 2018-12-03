import math

# =================================================================================
# =================================================================================
# Spur-gear generation script
# (c) James Gregson, 2012
# Free for all use, including commercial, but do not redistribute.
# Use at your own risk.
#
# Notes:
#  - seems to work well for pressure angles up to about 30 degrees
# =================================================================================
# =================================================================================

# compute the root diameter of a gear with a given pressure-angle (pa)
# number of teeth (N), and pitch (P)
def gears_root_diameter(pa, N, P):
    return (N - 2.5) / P


# compute the base diameter of a gear with a given pressure-angle (pa)
# number of teeth (N), and pitch (P)
def gears_base_diameter(pa, N, P):
    return gears_pitch_diameter(pa, N, P) * math.cos(pa * math.pi / 180.0)


# compute the outer diameter of a gear with a given pressure-angle (pa)
# number of teeth (N), and pitch (P)
def gears_outer_diameter(pa, N, P):
    return gears_pitch_diameter(pa, N, P) + 2.0 * gears_addendum(pa, N, P)


# compute the outer diameter of a gear with a given pressure-angle (pa)
# number of teeth (N), and pitch (P)
def gears_pitch_diameter(pa, N, P):
    return float(N) / float(P)


# compute the outer diameter of a gear with a given pressure-angle (pa)
# number of teeth (N) and pitch (P)
def gears_circular_pitch(pa, N, P):
    return math.pi / float(P)


# compute the circular tooth thickness of a gear with a given
# pressure-angle (pa), number of teeth (N) and pitch (P)
def gears_circular_tooth_thickness(pa, N, P, backlash=0.05):
    return gears_circular_pitch(pa, N, P) / (2.0 + backlash)


# compute the circular tooth angle of a gear with a given
# pressure-angle (pa), number of teeth (N) and pitch (P)
def gears_circular_tooth_angle(pa, N, P):
    return (
        gears_circular_tooth_thickness(pa, N, P) * 2.0 / gears_pitch_diameter(pa, N, P)
    )


# compute the addendum height for a gear with a given
# pressure-angle (pa), number of teeth (N) and pitch (P)
def gears_addendum(pa, N, P):
    return 1.0 / float(P)


# compute the dedendum depth for a gear with a given
# pressur-angle (pa), number of teeth (N) and pitch (P)
def gears_dedendum(pa, N, P):
    return 1.25 / float(P)


# generates an involute curve from a circle of radius r up to theta_max radians
# with a specified number of steps
def gears_generate_involute(r, r_max, theta_max, steps=30):
    dtheta = theta_max / float(steps)
    x = []
    y = []
    theta = []
    rlast = r
    for i in range(0, steps + 1):
        c = math.cos(i * dtheta)
        s = math.sin(i * dtheta)
        tx = r * (c + i * dtheta * s)
        ty = r * (s - i * dtheta * c)
        d = math.sqrt(tx * tx + ty * ty)
        if d > r_max:
            a = (r_max - rlast) / (d - rlast)
            tx = x[-1] * (1.0 - a) + tx * a
            ty = y[-1] * (1.0 - a) + ty * a
            ttheta = theta[-1] * (1.0 - a) + math.atan2(ty, tx) * a
            x.append(tx)
            y.append(ty)
            theta.append(ttheta)
            break
        else:
            x.append(tx)
            y.append(ty)
            theta.append(math.atan2(ty, tx))
    return x, y, theta


# returns the angle where an involute curve crosses a circle with a given radius
# or -1 on failure
def gears_locate_involute_cross_angle_for_radius(r, ix, iy, itheta):
    for i in range(0, len(ix) - 1):
        r2 = ix[i + 1] * ix[i + 1] + iy[i + 1] * iy[i + 1]
        if r2 > r * r:
            r1 = math.sqrt(ix[i] * ix[i] + iy[i] * iy[i])
            r2 = math.sqrt(r2)
            a = (r - r1) / (r2 - r1)
            return itheta[i] * (1.0 - a) + itheta[i + 1] * a
    return -1.0


# rotates the involute curve around the gear center in order to have the involute
# cross the x-axis at the pitch diameter
def gears_align_involute(Dp, ix, iy, itheta):
    theta = -gears_locate_involute_cross_angle_for_radius(Dp / 2.0, ix, iy, itheta)
    c = math.cos(theta)
    s = math.sin(theta)
    for i in range(0, len(ix)):
        tx = c * ix[i] - s * iy[i]
        ty = s * ix[i] + c * iy[i]
        ix[i] = tx
        iy[i] = ty
    return ix, iy


# reflects the input curve about the x-axis to generate the opposing face of
# a tooth
def gears_mirror_involute(ix, iy):
    tx = []
    ty = []
    for i in range(0, len(iy)):
        tx.append(ix[len(iy) - 1 - i])
        ty.append(-iy[len(iy) - 1 - i])
    return tx, ty


# rotates the input curve by a given angle (in radians)
def gears_rotate(theta, ix, iy):
    c = math.cos(theta)
    s = math.sin(theta)
    x = []
    y = []
    for i in range(0, len(ix)):
        tx = c * ix[i] - s * iy[i]
        ty = s * ix[i] + c * iy[i]
        x.append(tx)
        y.append(ty)
    return x, y


# translates the input curve by [dx, dy]
def gears_translate(dx, dy, ix, iy):
    x = []
    y = []
    for i in range(0, len(ix)):
        x.append(ix[i] + dx)
        y.append(iy[i] + dy)
    return x, y


# generates a single tooth profile of a spur gear
def gears_make_tooth(pa, N, P):
    ix, iy, itheta = gears_generate_involute(
        gears_base_diameter(pa, N, P) / 2.0,
        gears_outer_diameter(pa, N, P) / 2.0,
        math.pi / 2.1,
    )
    ix.insert(
        0, min(gears_base_diameter(pa, N, P) / 2.0, gears_root_diameter(pa, N, P) / 2.0)
    )
    iy.insert(0, 0.0)
    itheta.insert(0, 0.0)
    ix, iy = gears_align_involute(gears_pitch_diameter(pa, N, P), ix, iy, itheta)
    mx, my = gears_mirror_involute(ix, iy)
    mx, my = gears_rotate(gears_circular_tooth_angle(pa, N, P), mx, my)
    ix.extend(mx)
    iy.extend(my)
    return ix, iy


# generates a spur gear with a given pressure angle (pa),
# number of teeth (N) and pitch (P)
def gears_make_gear(pa, N, P):
    tx, ty = gears_make_tooth(pa, N, P)
    x = []
    y = []
    for i in range(0, N):
        rx, ry = gears_rotate(float(i) * 2.0 * math.pi / float(N), tx, ty)
        x.extend(rx)
        y.extend(ry)
    x.append(x[0])
    y.append(y[0])
    return x, y


# write output as svg, for laser-cutters, graphic design, etc.
def gears_svg_out(px, py, filename, scale=1.0):
    out = open(filename, "w")

    minx = min(px)
    maxx = max(px)
    miny = min(py)
    maxy = max(py)
    cenx = (minx + maxx) / 2.0
    ceny = (miny + maxy) / 2.0
    sx = (maxx - cenx) * 1.1
    sy = (maxy - ceny) * 1.1

    minx = scale * (cenx - sx)
    maxx = scale * (cenx + sx)
    miny = scale * (ceny - sy)
    maxy = scale * (ceny + sy)

    out.write('<?xml version="1.0" standalone="no" ?>\n')
    out.write(
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    )
    out.write(
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" x="%fpx" y="%fpx" width="%fpx" height="%fpx">\n'
        % (minx, miny, maxx - minx, maxy - miny)
    )
    out.write('<polyline style="fill:none;stroke:black;stroke-width:1" points="')

    for i in range(0, len(px)):
        out.write("%f,%f " % (scale * (px[i] + sx), scale * (py[i] + sy)))

    out.write('" />\n')
    out.write("</svg>\n")
    out.close()


# write output as dxf profile in x-y plane, for use with OpenSCAD
def gears_dxf_out(px, py, filename, scale=1.0):
    out = open(filename, "w")
    out.write("  0\n")
    out.write("SECTION\n")
    out.write("  2\n")
    out.write("HEADER\n")
    out.write("999\n")
    out.write("%s by gears.py\n" % filename)
    out.write("999\n")
    out.write("contact james.gregson@gmail.com for gears.py details\n")
    out.write("  0\n")
    out.write("ENDSEC\n")
    out.write("  0\n")
    out.write("SECTION\n")
    out.write("  2\n")
    out.write("TABLES\n")
    out.write("  0\n")
    out.write("ENDSEC\n")
    out.write("  0\n")
    out.write("SECTION\n")
    out.write("  2\n")
    out.write("BLOCKS\n")
    out.write("  0\n")
    out.write("ENDSEC\n")
    out.write("  0\n")
    out.write("SECTION\n")
    out.write("  2\n")
    out.write("ENTITIES\n")

    for i in range(0, len(px) - 1):
        out.write("  0\n")
        out.write("LINE\n")
        out.write("  8\n")
        out.write("  2\n")
        out.write(" 62\n")
        out.write("  4\n")
        out.write(" 10\n")
        out.write("%f\n" % (scale * px[i]))
        out.write(" 20\n")
        out.write("%f\n" % (scale * py[i]))
        out.write(" 30\n")
        out.write("0.0\n")
        out.write(" 11\n")
        out.write("%f\n" % (scale * px[i + 1]))
        out.write(" 21\n")
        out.write("%f\n" % (scale * py[i + 1]))
        out.write(" 31\n")
        out.write("0.0\n")

    out.write("  0\n")
    out.write("ENDSEC\n")
    out.write("  0\n")
    out.write("EOF\n")
    out.close()
