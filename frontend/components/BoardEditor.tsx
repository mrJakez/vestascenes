"use client";
import { post } from "@/utils/fetch";
import {
  BoardEditor,
  type IBoard,
  createBoard,
  ScheduleMessage,
  useToasts,
  ToastProvider,
} from "@vestaboard/installables";
import { useState } from "react";

export interface BoardEditorProps {
  backendUrl: string;
}

function Editor({ backendUrl }: BoardEditorProps) {
  const [boardValue, setBoardValue] = useState<IBoard>(createBoard);
  const [isScheduleMessageVisible, setScheduleMessageVisible] = useState(false);
  const { addToast } = useToasts();
  return (
    <>
      <BoardEditor
        boardValue={boardValue}
        setBoardValue={setBoardValue}
        onSend={() =>
          post({
            url: backendUrl + "/write",
            body: { mode: "set", boardValue },
            addToast,
            successMessage: "Board updated!",
            errorMessage: "Error updating board",
          })
        }
        onSchedule={() => setScheduleMessageVisible(true)}
      />
      <ScheduleMessage
        visible={isScheduleMessageVisible}
        onSend={(h, m, s) =>
          post({
            url: backendUrl,
            body: {
              mode: "schedule",
              scheduleIn: { h, m, s },
              boardValue,
            },
            addToast,
            successMessage: "Board updated!",
            errorMessage: "Error updating board",
          })
        }
        onCancel={() => setScheduleMessageVisible(false)}
      />
    </>
  );
}

export default function EditorWrapper(props: BoardEditorProps) {
  return (
    <div className="board-editor">
        <ToastProvider>
            <Editor {...props} />
        </ToastProvider>
    </div>
  );
}
