import { NextResponse } from "next/server";
import { createDemoReview } from "../../lib/demo-review";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!(file instanceof File)) {
      return NextResponse.json({ error: "A .txt hand history file is required." }, { status: 400 });
    }

    if (!file.name.toLowerCase().endsWith(".txt")) {
      return NextResponse.json({ error: "Only .txt files are supported in the free demo." }, { status: 400 });
    }

    const rawText = await file.text();

    if (rawText.trim().length < 40) {
      return NextResponse.json({ error: "This file looks too small to review." }, { status: 400 });
    }

    const review = createDemoReview({
      rawText,
      fileName: file.name,
    });

    return NextResponse.json(review);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "The upload could not be reviewed right now.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
