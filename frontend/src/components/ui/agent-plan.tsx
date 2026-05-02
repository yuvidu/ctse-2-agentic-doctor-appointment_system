"use client";

import { HEALTHCARE_PIPELINE_TASKS } from "@/data/healthcarePipelineTasks";
import type { Task } from "@/types/planTask";
import {
  AnimatePresence,
  LayoutGroup,
  motion,
  type Variants,
} from "framer-motion";
import {
  CheckCircle2,
  Circle,
  CircleAlert,
  CircleDotDashed,
  CircleX,
} from "lucide-react";
import { useEffect, useState } from "react";

export interface PlanProps {
  tasks?: Task[];
  onTasksChange?: React.Dispatch<React.SetStateAction<Task[]>>;
}

export default function Plan({
  tasks: controlledTasks,
  onTasksChange,
}: PlanProps = {}) {
  const [internalTasks, setInternalTasks] = useState<Task[]>(
    HEALTHCARE_PIPELINE_TASKS,
  );
  const isControlled = controlledTasks !== undefined;
  const tasks = isControlled ? controlledTasks! : internalTasks;
  const setTasks: React.Dispatch<React.SetStateAction<Task[]>> = isControlled
    ? (action) => {
        if (!onTasksChange) return;
        onTasksChange((prev) =>
          typeof action === "function"
            ? (action as (p: Task[]) => Task[])(prev)
            : action,
        );
      }
    : setInternalTasks;

  const [expandedTasks, setExpandedTasks] = useState<string[]>(["1", "2", "3"]);
  const [expandedSubtasks, setExpandedSubtasks] = useState<Record<string, boolean>>(
    {},
  );
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(true);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mq.matches);
    const listener = () => setPrefersReducedMotion(mq.matches);
    mq.addEventListener("change", listener);
    return () => mq.removeEventListener("change", listener);
  }, []);

  const toggleTaskExpansion = (taskId: string) => {
    setExpandedTasks((prev) =>
      prev.includes(taskId) ? prev.filter((id) => id !== taskId) : [...prev, taskId],
    );
  };

  const toggleSubtaskExpansion = (taskId: string, subtaskId: string) => {
    const key = `${taskId}-${subtaskId}`;
    setExpandedSubtasks((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const toggleTaskStatus = (taskId: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id !== taskId) return task;
        const statuses = [
          "completed",
          "in-progress",
          "pending",
          "need-help",
          "failed",
        ];
        const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
        const updatedSubtasks = task.subtasks.map((subtask) => ({
          ...subtask,
          status: newStatus === "completed" ? "completed" : subtask.status,
        }));
        return { ...task, status: newStatus, subtasks: updatedSubtasks };
      }),
    );
  };

  const toggleSubtaskStatus = (taskId: string, subtaskId: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id !== taskId) return task;
        const updatedSubtasks = task.subtasks.map((subtask) => {
          if (subtask.id !== subtaskId) return subtask;
          const newStatus =
            subtask.status === "completed" ? "pending" : "completed";
          return { ...subtask, status: newStatus };
        });
        const allSubtasksCompleted = updatedSubtasks.every(
          (s) => s.status === "completed",
        );
        return {
          ...task,
          subtasks: updatedSubtasks,
          status: allSubtasksCompleted ? "completed" : task.status,
        };
      }),
    );
  };

  const easeCurve = [0.2, 0.65, 0.3, 0.9] as const;
  const bounceCurve = [0.34, 1.56, 0.64, 1] as const;

  const taskVariants: Variants = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : -5 },
    visible: {
      opacity: 1,
      y: 0,
      transition: prefersReducedMotion
        ? { type: "tween", duration: 0.2 }
        : { type: "spring", stiffness: 500, damping: 30 },
    },
    exit: {
      opacity: 0,
      y: prefersReducedMotion ? 0 : -5,
      transition: { duration: 0.15 },
    },
  };

  const subtaskListVariants: Variants = {
    hidden: { opacity: 0, height: 0, overflow: "hidden" },
    visible: {
      height: "auto",
      opacity: 1,
      overflow: "visible",
      transition: {
        duration: 0.25,
        staggerChildren: prefersReducedMotion ? 0 : 0.05,
        when: "beforeChildren",
        ease: easeCurve,
      },
    },
    exit: {
      height: 0,
      opacity: 0,
      overflow: "hidden",
      transition: { duration: 0.2, ease: easeCurve },
    },
  };

  const subtaskVariants: Variants = {
    hidden: { opacity: 0, x: prefersReducedMotion ? 0 : -10 },
    visible: {
      opacity: 1,
      x: 0,
      transition: prefersReducedMotion
        ? { type: "tween", duration: 0.2 }
        : { type: "spring", stiffness: 500, damping: 25 },
    },
    exit: {
      opacity: 0,
      x: prefersReducedMotion ? 0 : -10,
      transition: { duration: 0.15 },
    },
  };

  const subtaskDetailsVariants: Variants = {
    hidden: { opacity: 0, height: 0, overflow: "hidden" },
    visible: {
      opacity: 1,
      height: "auto",
      overflow: "visible",
      transition: { duration: 0.25, ease: easeCurve },
    },
  };

  const statusBadgeVariants: Variants = {
    initial: { scale: 1 },
    animate: {
      scale: prefersReducedMotion ? 1 : [1, 1.08, 1],
      transition: { duration: 0.35, ease: bounceCurve },
    },
  };

  return (
    <div className="h-full overflow-auto bg-background/80 p-2 text-foreground backdrop-blur-md md:rounded-lg md:border md:border-border md:shadow">
      <motion.div
        className="overflow-hidden rounded-lg border border-border bg-card/95 shadow"
        initial={{ opacity: 0, y: 10 }}
        animate={{
          opacity: 1,
          y: 0,
          transition: { duration: 0.3, ease: easeCurve },
        }}
      >
        <LayoutGroup>
          <div className="overflow-hidden p-3 md:p-4">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Pipeline activity
            </p>
            <ul className="space-y-1 overflow-hidden">
              {tasks.map((task, index) => {
                const isExpanded = expandedTasks.includes(task.id);
                const isCompleted = task.status === "completed";

                return (
                  <motion.li
                    key={task.id}
                    className={index !== 0 ? "mt-1 pt-2" : ""}
                    initial="hidden"
                    animate="visible"
                    variants={taskVariants}
                  >
                    <motion.div className="group flex items-center rounded-md px-2 py-1.5 md:px-3">
                      <motion.div
                        className="mr-2 flex-shrink-0 cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleTaskStatus(task.id);
                        }}
                        whileTap={{ scale: 0.9 }}
                        whileHover={{ scale: 1.1 }}
                      >
                        <AnimatePresence mode="wait">
                          <motion.div
                            key={task.status}
                            initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                            exit={{ opacity: 0, scale: 0.8, rotate: 10 }}
                            transition={{ duration: 0.2, ease: [0.2, 0.65, 0.3, 0.9] }}
                          >
                            {task.status === "completed" ? (
                              <CheckCircle2 className="h-4 w-4 text-green-500" />
                            ) : task.status === "in-progress" ? (
                              <CircleDotDashed className="h-4 w-4 text-blue-500" />
                            ) : task.status === "need-help" ? (
                              <CircleAlert className="h-4 w-4 text-yellow-500" />
                            ) : task.status === "failed" ? (
                              <CircleX className="h-4 w-4 text-red-500" />
                            ) : (
                              <Circle className="h-4 w-4 text-muted-foreground" />
                            )}
                          </motion.div>
                        </AnimatePresence>
                      </motion.div>

                      <motion.div
                        className="flex min-w-0 flex-grow cursor-pointer items-center justify-between gap-2"
                        onClick={() => toggleTaskExpansion(task.id)}
                      >
                        <div className="mr-2 min-w-0 flex-1">
                          <span
                            className={`line-clamp-2 text-sm ${
                              isCompleted ? "text-muted-foreground line-through" : ""
                            }`}
                          >
                            {task.title}
                          </span>
                        </div>

                        <div className="flex flex-shrink-0 items-center space-x-2 text-xs">
                          {task.dependencies.length > 0 && (
                            <div className="mr-2 flex items-center">
                              <div className="flex flex-wrap gap-1">
                                {task.dependencies.map((dep, idx) => (
                                  <motion.span
                                    key={dep}
                                    className="rounded bg-secondary/40 px-1.5 py-0.5 text-[10px] font-medium text-secondary-foreground shadow-sm"
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.2, delay: idx * 0.05 }}
                                    whileHover={{
                                      y: -1,
                                      backgroundColor: "rgba(0,0,0,0.1)",
                                      transition: { duration: 0.2 },
                                    }}
                                  >
                                    {dep}
                                  </motion.span>
                                ))}
                              </div>
                            </div>
                          )}

                          <motion.span
                            className={`rounded px-1.5 py-0.5 capitalize ${
                              task.status === "completed"
                                ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
                                : task.status === "in-progress"
                                  ? "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
                                  : task.status === "need-help"
                                    ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300"
                                    : task.status === "failed"
                                      ? "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
                                      : "bg-muted text-muted-foreground"
                            }`}
                            variants={statusBadgeVariants}
                            initial="initial"
                            animate="animate"
                            key={task.status}
                          >
                            {task.status}
                          </motion.span>
                        </div>
                      </motion.div>
                    </motion.div>

                    <AnimatePresence mode="wait">
                      {isExpanded && task.subtasks.length > 0 && (
                        <motion.div
                          className="relative overflow-hidden"
                          variants={subtaskListVariants}
                          initial="hidden"
                          animate="visible"
                          exit="hidden"
                          layout
                        >
                          <div className="absolute top-0 bottom-0 left-[18px] border-l-2 border-dashed border-muted-foreground/30" />
                          <ul className="mb-1.5 ml-2 mr-1 mt-1 space-y-0.5 border-muted md:ml-3 md:mr-2">
                            {task.subtasks.map((subtask) => {
                              const subtaskKey = `${task.id}-${subtask.id}`;
                              const isSubtaskExpanded = expandedSubtasks[subtaskKey];

                              return (
                                <motion.li
                                  key={subtask.id}
                                  className="group flex flex-col py-0.5 pl-5 md:pl-6"
                                  onClick={() =>
                                    toggleSubtaskExpansion(task.id, subtask.id)
                                  }
                                  variants={subtaskVariants}
                                  initial="hidden"
                                  animate="visible"
                                  exit="exit"
                                  layout
                                >
                                  <motion.div
                                    className="flex flex-1 items-center rounded-md p-1"
                                    whileHover={{
                                      backgroundColor: "rgba(0,0,0,0.03)",
                                      transition: { duration: 0.2 },
                                    }}
                                    layout
                                  >
                                    <motion.div
                                      className="mr-2 flex-shrink-0 cursor-pointer"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        toggleSubtaskStatus(task.id, subtask.id);
                                      }}
                                      whileTap={{ scale: 0.9 }}
                                      whileHover={{ scale: 1.1 }}
                                      layout
                                    >
                                      <AnimatePresence mode="wait">
                                        <motion.div
                                          key={subtask.status}
                                          initial={{
                                            opacity: 0,
                                            scale: 0.8,
                                            rotate: -10,
                                          }}
                                          animate={{ opacity: 1, scale: 1, rotate: 0 }}
                                          exit={{ opacity: 0, scale: 0.8, rotate: 10 }}
                                          transition={{
                                            duration: 0.2,
                                            ease: [0.2, 0.65, 0.3, 0.9],
                                          }}
                                        >
                                          {subtask.status === "completed" ? (
                                            <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                                          ) : subtask.status === "in-progress" ? (
                                            <CircleDotDashed className="h-3.5 w-3.5 text-blue-500" />
                                          ) : subtask.status === "need-help" ? (
                                            <CircleAlert className="h-3.5 w-3.5 text-yellow-500" />
                                          ) : subtask.status === "failed" ? (
                                            <CircleX className="h-3.5 w-3.5 text-red-500" />
                                          ) : (
                                            <Circle className="h-3.5 w-3.5 text-muted-foreground" />
                                          )}
                                        </motion.div>
                                      </AnimatePresence>
                                    </motion.div>

                                    <span
                                      className={`cursor-pointer text-xs md:text-sm ${
                                        subtask.status === "completed"
                                          ? "text-muted-foreground line-through"
                                          : ""
                                      }`}
                                    >
                                      {subtask.title}
                                    </span>
                                  </motion.div>

                                  <AnimatePresence mode="wait">
                                    {isSubtaskExpanded && (
                                      <motion.div
                                        className="mt-1 ml-1.5 overflow-hidden border-l border-dashed border-foreground/20 pl-4 text-xs text-muted-foreground md:pl-5"
                                        variants={subtaskDetailsVariants}
                                        initial="hidden"
                                        animate="visible"
                                        exit="hidden"
                                        layout
                                      >
                                        <p className="py-1">{subtask.description}</p>
                                        {subtask.tools && subtask.tools.length > 0 && (
                                          <div className="mb-1 mt-0.5 flex flex-wrap items-center gap-1.5">
                                            <span className="font-medium text-muted-foreground">
                                              Tools:
                                            </span>
                                            <div className="flex flex-wrap gap-1">
                                              {subtask.tools.map((tool, idx) => (
                                                <motion.span
                                                  key={tool}
                                                  className="rounded bg-secondary/40 px-1.5 py-0.5 text-[10px] font-medium text-secondary-foreground shadow-sm"
                                                  initial={{ opacity: 0, y: -5 }}
                                                  animate={{
                                                    opacity: 1,
                                                    y: 0,
                                                    transition: {
                                                      duration: 0.2,
                                                      delay: idx * 0.05,
                                                    },
                                                  }}
                                                  whileHover={{
                                                    y: -1,
                                                    backgroundColor: "rgba(0,0,0,0.1)",
                                                    transition: { duration: 0.2 },
                                                  }}
                                                >
                                                  {tool}
                                                </motion.span>
                                              ))}
                                            </div>
                                          </div>
                                        )}
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </motion.li>
                              );
                            })}
                          </ul>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.li>
                );
              })}
            </ul>
          </div>
        </LayoutGroup>
      </motion.div>
    </div>
  );
}
