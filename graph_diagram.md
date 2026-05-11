# LangGraph Agent Architecture (Detailed)

```mermaid
graph TD
    %% Khởi đầu
    START((START)) --> intake[intake: Clean PII]
    intake --> classify{classify: Intent?}

    %% Các nhánh chính từ classify
    classify -- "Simple" --> answer[answer: Response]
    classify -- "Missing Info" --> clarify[clarify: Ask User]
    classify -- "Risky" --> risky_action[risky_action: Prepare]
    classify -- "Error" --> retry[retry: Inc Attempt]
    classify -- "Tool" --> fan_out{fan_out: Multi-intent?}

    %% Nhánh Parallel Fan-out
    fan_out -- "Parallel Send" --> shipping_tool[shipping_tool]
    fan_out -- "Parallel Send" --> inventory_tool[inventory_tool]
    fan_out -- "Single Send" --> tool[tool: Default]

    %% Hội tụ sau Tool
    shipping_tool --> evaluate
    inventory_tool --> evaluate
    tool --> evaluate

    %% Vòng lặp Retry & Evaluation
    evaluate{evaluate: Success?}
    evaluate -- "Retry" --> retry
    evaluate -- "Fail (Dead Letter)" --> dead_letter[dead_letter]
    evaluate -- "Done" --> answer

    retry --> classify

    %% Nhánh Phê duyệt (HITL)
    risky_action --> approval{approval: HITL Interrupt}
    approval -- "Approved" --> evaluate
    approval -- "Rejected/Edit" --> evaluate

    %% Kết thúc
    answer --> finalize[finalize: Audit Event]
    clarify --> finalize
    dead_letter --> finalize
    finalize --> END((END))

    %% Chú thích phong cách
    classDef highlight fill:#f9f,stroke:#333,stroke-width:2px;
    class fan_out,approval,evaluate highlight;
```
