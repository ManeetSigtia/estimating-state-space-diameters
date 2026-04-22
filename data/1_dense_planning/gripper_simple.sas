begin_version
3
end_version
begin_metric
1
end_metric
begin_variable
var0_robot
-1
2
Atom at-robby(rooma)
Atom at-robby(roomb)
end_variable
begin_variable
var1_left_hand
-1
2
Atom free(left)
Atom carry(ball1, left)
end_variable
begin_variable
var2_ball1
-1
3
Atom at(ball1, rooma)
Atom at(ball1, roomb)
Atom carried(ball1, left)
end_variable
begin_state
0
0
0
end_state
begin_goal
1
2 1
end_goal
begin_operator
move rooma roomb
0
1
0 0 0 1
1
end_operator
begin_operator
move roomb rooma
0
1
0 0 1 0
1
end_operator
begin_operator
pick ball1 rooma left
1
0 0
2
0 1 0 1
0 2 0 2
1
end_operator
begin_operator
drop ball1 roomb left
1
0 1
2
0 1 1 0
0 2 2 1
1
end_operator
0