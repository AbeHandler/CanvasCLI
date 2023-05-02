visible when='-tt':
  python -m src.cli -v {{when}}

checkin:
  python -m src.cli -checkin

participation target:
  python -m  src.cli grade -participation -assignment_id {{target}}

quiz day="":
  python -m src.cli -q {{day}}

students:
  python -m src.cli -students

#                       _ _             
#    __ _ _ __ __ _  __| (_)_ __   __ _ 
#   / _` | '__/ _` |/ _` | | '_ \ / _` |
#  | (_| | | | (_| | (_| | | | | | (_| |
#   \__, |_|  \__,_|\__,_|_|_| |_|\__, |
#   |___/                         |___/ 
#                                       

autograde notebook_name canvas_name:
  #!/usr/bin/env bash
  python -m src.cli assignment -cn '{{canvas_name}}' -download -nbn '{{notebook_name}}' -autograde

ta target:
  rsync -r /Users/abe/everything/teaching/S2023/3220/3220 /Users/abe/BAIM3220FeedbackReports -v --ignore-existing --include="*/" --include="*.html" --exclude="*" 
  cd /Users/abe/BAIM3220FeedbackReports && git status  | grep {{target}} | grep -v "new file" | awk -F" " '{print $1}' | parallel -j 1 "git add {}" && git commit -m {{target}} && git push origin main

reports notebook_name canvas_name group_name='Exercises':
  python -m src.cli assignment -reports -nbn "{{notebook_name}}" -g "{{group_name}}" -cn "{{canvas_name}}"

perfects notebook_name canvas_name group_name='Exercises':
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}" -perfects

skipped notebook_name canvas_name group_name='Exercises':
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}"  -skipped

missed_challenge notebook_name canvas_name group_name='Exercises':
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}"  -missed_challenge

# basically a wrapper over the three prior grading commands
run_grader notebook_name canvas_name group_name='Exercises':
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}" -perfects
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}"  -skipped
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}"  -missed_challenge