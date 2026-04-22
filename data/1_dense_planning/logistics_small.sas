begin_version
3
end_version
begin_metric
0
end_metric
5
begin_variable
var0
-1
2
Atom at(truck2, locb1)
Atom at(truck2, locb2)
end_variable
begin_variable
var1
-1
2
Atom at(truck1, loca1)
Atom at(truck1, loca2)
end_variable
begin_variable
var2
-1
2
Atom at(plane1, loca1)
Atom at(plane1, locb1)
end_variable
begin_variable
var3
-1
7
Atom at(package2, loca1)
Atom at(package2, loca2)
Atom at(package2, locb1)
Atom at(package2, locb2)
Atom in(package2, plane1)
Atom in(package2, truck1)
Atom in(package2, truck2)
end_variable
begin_variable
var4
-1
7
Atom at(package1, loca1)
Atom at(package1, loca2)
Atom at(package1, locb1)
Atom at(package1, locb2)
Atom in(package1, plane1)
Atom in(package1, truck1)
Atom in(package1, truck2)
end_variable
0
begin_state
0
0
0
3
1
end_state
begin_goal
2
3 1
4 3
end_goal
30
begin_operator
drive-truck truck1 loca1 loca2 citya
0
1
0 1 0 1
1
end_operator
begin_operator
drive-truck truck1 loca2 loca1 citya
0
1
0 1 1 0
1
end_operator
begin_operator
drive-truck truck2 locb1 locb2 cityb
0
1
0 0 0 1
1
end_operator
begin_operator
drive-truck truck2 locb2 locb1 cityb
0
1
0 0 1 0
1
end_operator
begin_operator
fly-airplane plane1 loca1 locb1
0
1
0 2 0 1
1
end_operator
begin_operator
fly-airplane plane1 locb1 loca1
0
1
0 2 1 0
1
end_operator
begin_operator
load-airplane package1 plane1 loca1
1
2 0
1
0 4 0 4
1
end_operator
begin_operator
load-airplane package1 plane1 locb1
1
2 1
1
0 4 2 4
1
end_operator
begin_operator
load-airplane package2 plane1 loca1
1
2 0
1
0 3 0 4
1
end_operator
begin_operator
load-airplane package2 plane1 locb1
1
2 1
1
0 3 2 4
1
end_operator
begin_operator
load-truck package1 truck1 loca1
1
1 0
1
0 4 0 5
1
end_operator
begin_operator
load-truck package1 truck1 loca2
1
1 1
1
0 4 1 5
1
end_operator
begin_operator
load-truck package1 truck2 locb1
1
0 0
1
0 4 2 6
1
end_operator
begin_operator
load-truck package1 truck2 locb2
1
0 1
1
0 4 3 6
1
end_operator
begin_operator
load-truck package2 truck1 loca1
1
1 0
1
0 3 0 5
1
end_operator
begin_operator
load-truck package2 truck1 loca2
1
1 1
1
0 3 1 5
1
end_operator
begin_operator
load-truck package2 truck2 locb1
1
0 0
1
0 3 2 6
1
end_operator
begin_operator
load-truck package2 truck2 locb2
1
0 1
1
0 3 3 6
1
end_operator
begin_operator
unload-airplane package1 plane1 loca1
1
2 0
1
0 4 4 0
1
end_operator
begin_operator
unload-airplane package1 plane1 locb1
1
2 1
1
0 4 4 2
1
end_operator
begin_operator
unload-airplane package2 plane1 loca1
1
2 0
1
0 3 4 0
1
end_operator
begin_operator
unload-airplane package2 plane1 locb1
1
2 1
1
0 3 4 2
1
end_operator
begin_operator
unload-truck package1 truck1 loca1
1
1 0
1
0 4 5 0
1
end_operator
begin_operator
unload-truck package1 truck1 loca2
1
1 1
1
0 4 5 1
1
end_operator
begin_operator
unload-truck package1 truck2 locb1
1
0 0
1
0 4 6 2
1
end_operator
begin_operator
unload-truck package1 truck2 locb2
1
0 1
1
0 4 6 3
1
end_operator
begin_operator
unload-truck package2 truck1 loca1
1
1 0
1
0 3 5 0
1
end_operator
begin_operator
unload-truck package2 truck1 loca2
1
1 1
1
0 3 5 1
1
end_operator
begin_operator
unload-truck package2 truck2 locb1
1
0 0
1
0 3 6 2
1
end_operator
begin_operator
unload-truck package2 truck2 locb2
1
0 1
1
0 3 6 3
1
end_operator
0
