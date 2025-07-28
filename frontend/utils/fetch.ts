import type { IToastContext } from "@vestaboard/installables/lib/components/Toast/ToastContext";

export const post = ({
  url,
  body,
  addToast,
  successMessage = "Success!",
  errorMessage = "Error!",
}: {
  url: string;
  body: unknown;
  addToast?: IToastContext["addToast"];
  successMessage?: string;
  errorMessage?: string;
}) =>
  fetch(url, {
    method: "POST",
    // mode: "no-cors",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  })
    .then((res) => {
      if (res.ok) {
        addToast?.(successMessage, { appearance: "success" });
      } else {
        throw new Error("Server error");
      }
    })
    .catch(() => addToast?.(errorMessage, { appearance: "error" }));
