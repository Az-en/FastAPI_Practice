# tests/unit/test_course_service.py
import pytest
from unittest.mock import Mock
from uuid import uuid4
from src.services.course_service import CourseService
from src.schemas.course import CourseUpdate
from fastapi import HTTPException

def test_ensure_instructor_rejects_non_teacher():
    user_repo = Mock()      # fake repo
    user_repo.get_user.return_value = Mock(role="student")      # returns a User object?? with role=student
    course_repo = Mock()    # fake repo

    # the fake repos needed to create an instance of CourseService
    service = CourseService(user_repo=user_repo, course_repo=course_repo)

    with pytest.raises(HTTPException): 
        service._ensure_instructor(uuid4())

def test_ensure_instructor_raises_not_found_for_missing_user():
    user_repo = Mock()
    user_repo.get_user.return_value = None
    course_repo = Mock()
    service = CourseService(user_repo=user_repo, course_repo=course_repo)

    with pytest.raises(HTTPException):
        service._ensure_instructor(uuid4())

def test_update_course_change_given_values():
    """ 
    Test to make sure that when updating a course only the given values are updated.
    Since this is the Service layer, we verify that the Service delegates the partial 
    update correctly to the Repository without triggering unnecessary validations.
    We are testing the following(I fell these should be individual tests):
        1.The service bypasses the instructor validation if an instructor_id is not provided.
        2.The service correctly passes the course_in data straight to the repository.
        3.The service returns whatever the repository gives back.
    """
    course_repo = Mock()
    user_repo = Mock()
    service = CourseService(user_repo=user_repo,course_repo=course_repo)
    
    target_course_id = uuid4()
    course_in_data = CourseUpdate(title="New Course Title")
    # Simulate the Repository returning the merged/updated database object
    updated_course_mock = Mock(
        id=target_course_id, 
        title="New Course Title", 
        description="Old Description", # The old value remains
        instructor_id=uuid4()
    )
    course_repo.update_course.return_value = updated_course_mock

    # 3. Execution
    result = service.update_course(course_id=target_course_id, course_in=course_in_data)

    # 4. Assertions
    # Ensure the repository was called with the exact ID and partial update schema
    course_repo.update_course.assert_called_once_with(
        course_id=target_course_id, 
        course_in=course_in_data
    )
    course_in_data = CourseUpdate(title="New Course Title")
    
    # Ensure the instructor validation was skipped since instructor_id was None
    user_repo.get_user.assert_not_called()
    
    # Ensure the service successfully returns the updated object from the repository
    assert result == updated_course_mock
    assert result.title == "New Course Title"
    assert result.description == "Old Description"