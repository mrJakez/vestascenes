
import styles from "./page.module.css";
import { unstable_noStore } from "next/cache";
import TabBarClientContainer from "@/components/TabBarClientContainer";

export default function Home() {
  unstable_noStore();
  return (
    <div className={styles.page}>
        <h1>vestascenes</h1>
        <main className={styles.main}>
            <TabBarClientContainer />
        </main>
    </div>
  );
}