import styles from "./page.module.css";
import { unstable_noStore } from "next/cache";
import TabBarClientContainer from "@/components/TabBarClientContainer";

export default function HomeAssistantPage() {
  unstable_noStore();
  return (
    <div className={styles.page}>
      <main className={styles.main}>
            <TabBarClientContainer />
      </main>
    </div>
  );
}