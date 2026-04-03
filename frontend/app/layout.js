import "./globals.css";
import { Navigation } from "@/components/layout/Navigation";

export const metadata = {
  title: "InsureGig - Parametric Insurance for Gig Workers",
  description: "Instant parametric insurance for platform workers against weather, pollution, and operational disruptions",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-gray-50 dark:bg-gray-900">
        <Navigation />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
