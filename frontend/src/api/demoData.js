export function demoDelay(ms = 400) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const DEMO_BORROWERS = [
  {
    loan_id: 101,
    borrower_id: 1,
    name: 'Ayesha Khan',
    phone: '+923001234567',
    loan_number: 'CR-0412',
    installment_amount: 25000,
    next_due_date: new Date().toISOString().slice(0, 10),
    due_status: 'due_today',
    days_overdue: 0,
  },
  {
    loan_id: 102,
    borrower_id: 2,
    name: 'Rizwan Mahmood',
    phone: '+923009876543',
    loan_number: 'CR-0389',
    installment_amount: 40000,
    next_due_date: new Date(Date.now() - 3 * 86400000).toISOString().slice(0, 10),
    due_status: 'overdue',
    days_overdue: 3,
  },
];

export function getDemoBorrowers() {
  return DEMO_BORROWERS;
}

export function getDemoMetrics() {
  return {
    active_loans: 5,
    due_today: 1,
    overdue: 1,
    reminders_sent_today: 7,
  };
}

export function getDemoPolicyAnswer(question) {
  return {
    answer: `Based on the policy manual, the answer references your question on “${question}”. Commercial LTV is capped at 70% and late-payment grace is five business days. [§2.1 Maximum LTV]`,
    context_used: 'Demo policy context',
  };
}

export function getDemoReminderPreview(payload) {
  return {
    message: `Assalam-o-Alaikum ${payload.borrower_name}, loan ${payload.loan_number} installment ${payload.amount} is due. Please arrange payment. — Credit Team`,
  };
}

export function getDemoReminderSend(loanIds) {
  return {
    total: loanIds.length,
    sent: loanIds.length,
    failed: 0,
    results: loanIds.map((id) => ({ loan_id: id, status: 'sent', sid: `SIM-${id}` })),
  };
}

export function getDemoLogin() {
  return {
    access_token: 'demo-access-token',
    refresh_token: 'demo-refresh-token',
    user: {
      id: 2,
      email: 'analyst@bank.pk',
      full_name: 'Kashif Ahmed',
      role: 'analyst',
    },
  };
}
