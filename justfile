visible:
  python -m src.cli -v -tt

checkin:
  python -m src.cli -checkin

participation target:
  python -m  src.cli grade -participation -assignment_id {{target}}

quiz target:
  python -m src.cli {{target}} -quiz

autograde canvas_name notebook_name:
  python -m src.cli assignment -cn '{{canvas_name}}' -download -nbn '{{notebook_name}}' -autograde

ta:
  rsync -r /Users/abe/everything/teaching/S2023/3220/3220 /Users/abe/BAIM3220FeedbackReports -v --ignore-existing --include="*/" --include="*.html" --exclude="*" 
  cd /Users/abe/CanvasCLI/3220reports