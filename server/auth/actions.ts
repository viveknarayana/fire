"use server";

import { createClient } from "@/utils/supabase/server";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { z } from "zod";

export async function signInWithGoogle() {
	"use server";
	const orign = (await headers()).get("origin")!;

	const supabase = await createClient();
	const { data, error } = await supabase.auth.signInWithOAuth({
		provider: "google",
		options: { redirectTo: `${orign}/auth/callback` },
	});

  console.log(`${orign}/auth/callback`)

  console.log(data)

	if (error) {
		console.error(error);
	} else {
		return redirect(data.url);
	}
}

export async function signInWithLinkedIn() {
	"use server";
	const supabase = await createClient();
	const { data, error } = await supabase.auth.signInWithOAuth({
		provider: "linkedin_oidc",
		options: {
			redirectTo: `${process.env.NEXT_PUBLIC_SUPABASE_URL}"/auth/callback"`,
		},
	});
	if (error) {
		console.error(error);
	} else {
		return redirect(data.url);
	}
}

export async function registerWithEmail(
	prevState: { message: string },
	formData: FormData
): Promise<{ message: string }> {
  const schema = z.object({
    email: z.string().email({ message: "Invalid email address" }),
    password: z
      .string()
      .min(8, { message: "Password must be at least 8 characters" }),
    confirmPassword: z.string(),
    firstName: z.string(),
    lastName: z.string(),
  });

  const parse = schema.safeParse({
    email: formData.get("email")?.toString(),
    password: formData.get("password")?.toString(),
    confirmPassword: formData.get("confirmPassword")?.toString(),
    firstName: formData.get("firstName")?.toString(),
    lastName: formData.get("lastName")?.toString(),
  });

  if (!parse.success) {
    console.log(parse.error.issues);
    return {
      message: parse.error.issues.map((issue) => issue.message).join(", "),
    };
  }
  const { email, password, confirmPassword, firstName, lastName } = parse.data;

	if (password !== confirmPassword) {
		return { message: "Passwords do not match." };
	}

	const supabase = await createClient();
	const { data, error } = await supabase.auth.signUp({
		email: email,
		password: password,
		options: {
			data: {
				full_name: firstName + " " + lastName
			},
		},
	});

	if (error) {
		console.error("Registration failed:", error.message);
		return { message: "Failed to register." };
	} else if (data.user) {
		redirect("/dashboard");
	} else {
		return { message: "Failed to register." };
	}
}

export async function signInWithEmail(
	prevState: { message: string },
	formData: FormData
): Promise<{ message: string }> {
  const schema = z.object({
    email: z.string().email({ message: "Invalid email address" }),
    password: z
      .string()
      .min(8, { message: "Password must be at least 8 characters" }),
  });

	const parse = schema.safeParse({
		email: formData.get("email"),
		password: formData.get("password"),
	});

  if (!parse.success) {
    return {
      message: parse.error.issues.map((issue) => issue.message).join(", "),
    };
  }
  const { email, password } = parse.data;

	const supabase = await createClient();
	const { data, error } = await supabase.auth.signInWithPassword({
		email,
		password,
	});

	if (error) {
		console.error("Sign in failed:", error.message);
		return { message: error.message };
	} else if (data.user) {
		redirect("/dashboard");
	} else {
		return { message: "Failed to sign in." };
	}
}

export async function signOut() {
	"use server";
	const orign = (await headers()).get("origin")!;
	console.log("Signing out!")
	const supabase = await createClient();
	const { error } = await supabase.auth.signOut();

	if (error) {
		console.error(error);
	} else {
		return redirect(orign);
	}
}
