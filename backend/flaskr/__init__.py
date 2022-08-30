import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def format_categories():
    result = Category.query.order_by(Category.id).all()
    formatted = [category.format() for category in result]
    categories = {}
    for category in formatted:
        categories[category["id"]] = category["type"]
    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the DONEs
    """
    # CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        categories = format_categories()

        return jsonify({"success": True, "categories": categories})

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        query = Question.query.order_by(Question.id).all()

        questions = [question.format() for question in query]
        current_questions = questions[start:end]
        categories = format_categories()
        if len(current_questions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(questions),
                "categories": categories,
                "current_category": None,
            }
        )

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({"success": True, "deleted": id})
        except:
            abort(422)

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        searchTerm = body.get("searchTerm", None)
        try:
            if searchTerm:
                query = (
                    Question.query.order_by(Question.id)
                    .filter(Question.question.ilike(f"%{searchTerm}%"))
                    .all()
                )
                page = request.args.get("page", 1, type=int)
                start = (page - 1) * QUESTIONS_PER_PAGE
                end = start + QUESTIONS_PER_PAGE

                questions = [question.format() for question in query]
                current_questions = questions[start:end]
                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(questions),
                        "current_category": None,
                    }
                )
            else:
                if not question or not answer or not category or not difficulty:
                    abort(400)
                new_question = Question(
                    question=question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty,
                )
                new_question.insert()

                return jsonify(
                    {
                        "success": True,
                    }
                )

        except:
            abort(422)

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_by_category(category_id):
        query = (
            Question.query.filter_by(category=category_id).order_by(Question.id).all()
        )
        questions = [question.format() for question in query]

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "total_questions": len(questions),
                "current_category": None,
            }
        )

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def get_quizzes():
        try:
            past_questions = request.get_json().get("previous_questions", None)
            category = request.get_json().get("quiz_category", None)
            if category and category["id"]:
                query = Question.query.filter_by(category=category["id"]).all()
            else:
                query = Question.query.all()
            questions = [question.format() for question in query]
            if len(questions) == 0:
                abort(404)
            if past_questions:
                for question in list(questions):
                    if question["id"] in past_questions:
                        questions.remove(question)

            question = None
            if len(questions):
                question = random.choice(questions)

            return jsonify({"success": True, "question": question})
        except:
            abort(400)

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(500)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 500, "message": "server error"}),
            500,
        )

    return app
