import pandas as pd
import json, requests
from datetime import datetime, timedelta
from canvasapi import Canvas
from canvas_cli import get_api


def get_peer_reviews(course, assignment_id):
    '''
    Get the peer review scores for an assignment_id for a course
    
    thanks to Brian Keegan for this code
    
    '''
        
    _assignment = course.get_assignment(assignment_id)

    # Get peer reviews
    _pr_l = [{'submitter_user_id':_pr.user_id,
             'assessor_user_id':_pr.assessor_id,
             'asset_id':_pr.asset_id,
             'state':_pr.workflow_state}
            for _pr in _assignment.get_peer_reviews()]

    # Get peer review assessments
    _assignment_rubric = _assignment.rubric_settings['id']
    _ra_l = [{'asset_id':_a['artifact_id'],
             'assessor_user_id':_a['assessor_id'],
             'score':_a['score']}
            for _a in course.get_rubric(_assignment_rubric,include='peer_assessments',style='full').assessments]

    # Combine
    _assignment_pr_assessment_df = pd.merge(
        left = pd.DataFrame(_pr_l),
        right = pd.DataFrame(_ra_l),
        left_on = ['assessor_user_id','asset_id'],
        right_on = ['assessor_user_id','asset_id'],
        how = 'outer'
        )
    
    return _assignment_pr_assessment_df

def assign_grades_if_peer_review_exists(course, assignment_id):
    '''
    Assign a student's grade based on peer review, if it exists
    
    thanks to Brian Keegan for this code
    '''
    _assignment_pr_assessment_df = get_peer_reviews(course, assignment_id)
    for r in _assignment_pr_assessment_df.to_dict('records'):
        if r['state'] == 'completed':
            print(r['submitter_user_id'], r["score"])
            #_assignment.get_submission(r['submitter_user_id']).edit(submission={'posted_grade':r['score']})
        else:
            print("[*] Warning no review {}".format(r))

def find_missing_peer_reviews(course, assignment_id):
    '''
    Assign a student's grade based on peer review, if it exists
    
    thanks to Brian Keegan for this code
    '''
    _assignment_pr_assessment_df = get_peer_reviews(course, assignment_id)
    out = []
    for r in _assignment_pr_assessment_df.to_dict('records'):
        if r['state'] != 'completed':
            out.append(r)
    return out

def deduct_for_missing_reviews(course, assignment_id):
    '''
    Assign a student's grade based on peer review, if it exists
    
    thanks to Brian Keegan for this code
    '''
    
    missing = find_missing_peer_reviews(course, assignment_id)
    
    _assignment = course.get_assignment(assignment_id)

    # Deduct points from submissions missing peer reviews
    for r in missing:
        try:
            _current_score = _assignment.get_submission(r['assessor_user_id']).score
            _penalty = round(_assignment.points_possible * .1)
            _penalty_score = _current_score - _penalty
            
            #_assignment.get_submission(r['assessor_user_id']).edit(submission={'posted_grade':_penalty_score},
            #                                                       comment={'text_comment':"Incomplete peer review, grade dropped by 10%"})
        except TypeError:
            print(r, _assignment.get_submission(r['assessor_user_id']))
            print("Assessor {0}'s assignment has not been submitted/graded".format(r['assessor_user_id']))
            pass


if __name__ == "__main__":

    c = get_api()
    course = c.get_course(70121)
    #get_peer_reviews(course, assignment_id=956224)
    assign_grades_if_peer_review_exists(course, assignment_id=956224)
    deduct_for_missing_reviews(course, assignment_id=956224)