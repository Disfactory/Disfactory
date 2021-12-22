class DocumentDisplayStatusConst:
    REPORTED = "已檢舉"
    AUDIT_SCHEDULED = "已排程稽查"
    COMMUNICATION_PERIOD = "陳述意見期"
    WORK_STOPPED = "已勒令停工"
    POWER_OUTING = "已發函斷電"
    POWER_OUTED = "已斷電"
    DEMOLITION_SCHEDULED = "已排程拆除"
    DEMOLISHED = "已拆除"
    WAITING_FOR_NEW_EVIDENCE = "等待新事證"
    IN_PROGRESS = "處理中"
    OPEN = "未處理"

    STATUS_LIST = [REPORTED,
                   AUDIT_SCHEDULED,
                   COMMUNICATION_PERIOD,
                   WORK_STOPPED,
                   POWER_OUTING,
                   DEMOLITION_SCHEDULED,
                   DEMOLISHED,
                   WAITING_FOR_NEW_EVIDENCE]

    STATUS_LIST_ENRICHMENT = STATUS_LIST + [IN_PROGRESS]
