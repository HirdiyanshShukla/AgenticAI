import json
import os

from research import research


QUESTIONS_FILE = "evals/questions.json"
BASELINE_DIR = "evals/baseline"


def main():

    # Load evaluation questions
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    # Create baseline directory
    os.makedirs(BASELINE_DIR, exist_ok=True)

    total = len(questions)

    print(f"Running {total} evaluation questions...\n")

    for item in questions:

        question_id = item["id"]
        question = item["question"]

        print("\n" + "=" * 60)
        print(f"Evaluation {question_id}/{total}")
        print("=" * 60)

        # Run research pipeline
        report = research(question)

        # Store question + expected criteria + generated report
        result = {
            "id": question_id,
            "type": item["type"],
            "question": question,
            "expected": item["expected"],
            "report": report
        }

        # Save result
        output_file = os.path.join(
            BASELINE_DIR,
            f"{question_id:03d}.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(f"\nSaved: {output_file}")

    print("\n" + "=" * 60)
    print("BASELINE COMPLETE")
    print("=" * 60)

    print(f"Saved {total} evaluation results.")
    print(f"Location: {BASELINE_DIR}")


if __name__ == "__main__":
    main()