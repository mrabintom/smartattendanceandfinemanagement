// Sidebar Toggle
const sidebarToggle = document.getElementById('sidebarToggle');
if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-open');
    });
}

// Chart.js initialization for Attendance Trend
const attendanceChartElem = document.getElementById('attendanceChart');
if (attendanceChartElem) {
    const attendanceCtx = attendanceChartElem.getContext('2d');
    new Chart(attendanceCtx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Total Present',
                data: [480, 475, 490, 485, 495, 470, 450],
                borderColor: '#6366f1',
                tension: 0.3,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Students'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Day of the Week'
                    }
                }
            }
        }
    });
}

// Chart.js initialization for Fine Status Doughnut Chart
const fineChartElem = document.getElementById('fineChart');
if (fineChartElem) {
    const fineCtx = fineChartElem.getContext('2d');
    new Chart(fineCtx, {
        type: 'doughnut',
        data: {
            labels: ['Present', 'Absent'],
            datasets: [{
                data: [10, 0 ],
                backgroundColor: ['#22c55e', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 20
                    }
                },
            }
        }
    });
}




// Sidebar Toggle
document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.body.classList.toggle('sidebar-open');
});




document.addEventListener('DOMContentLoaded', () => {

    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            document.body.classList.toggle('sidebar-open');
        });
    }

    // Dummy data and metric updates
    const totalTeachers = 15;
    const pendingApprovals = 5;
    const totalStudents = 500;
    const totalFines = 12500;

    document.getElementById('total-teachers').textContent = totalTeachers;
    document.getElementById('pending-teacher-approvals').textContent = pendingApprovals;
    document.getElementById('total-students').textContent = totalStudents;
    document.getElementById('total-fines').textContent = `₹${totalFines}`;

    // Dummy table actions (Approve/Delete)
    const teacherApprovalTable = document.getElementById('teacherApprovalTable');
    if (teacherApprovalTable) {
        teacherApprovalTable.addEventListener('click', (e) => {
            if (e.target.closest('.approve-btn')) {
                const row = e.target.closest('tr');
                const teacherName = row.cells[1].textContent;
                console.log(`Approved teacher: ${teacherName}`);
                row.remove();
                showToast('Teacher Approved', `${teacherName} has been approved successfully.`);
            } else if (e.target.closest('.delete-approval-btn')) {
                const row = e.target.closest('tr');
                const teacherName = row.cells[1].textContent;
                console.log(`Deleted pending teacher: ${teacherName}`);
                row.remove();
                showToast('Teacher Deleted', `${teacherName} has been removed from pending approvals.`, 'danger');
            }
        });
    }

    const teachersTable = document.getElementById('teachersTable');
    if (teachersTable) {
        teachersTable.addEventListener('click', (e) => {
            if (e.target.closest('.delete-teacher-btn')) {
                const row = e.target.closest('tr');
                const teacherName = row.cells[1].textContent;
                console.log(`Deleted teacher: ${teacherName}`);
                row.remove();
                showToast('Teacher Removed', `${teacherName} has been removed from the system.`, 'danger');
            }
        });
    }

    // Add dummy teacher button
    const addDummyTeacherBtn = document.getElementById('addDummyTeacher');
    if (addDummyTeacherBtn) {
        addDummyTeacherBtn.addEventListener('click', () => {
            const newTeacher = {
                id: 'T' + Math.floor(Math.random() * 10000),
                name: 'New Teacher',
                email: 'new.teacher@email.com',
                department: 'New Dept',
                status: 'Active'
            };
            addTeacherToTable(newTeacher);
            showToast('Teacher Added', 'A new dummy teacher has been added.', 'success');
        });
    }

    // Function to add a new teacher row
    function addTeacherToTable(teacher) {
        const tableBody = document.getElementById('teachersTable').querySelector('tbody');
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${teacher.id}</td>
            <td>${teacher.name}</td>
            <td>${teacher.email}</td>
            <td>${teacher.department}</td>
            <td><span class="badge bg-success">${teacher.status}</span></td>
            <td><button class="btn btn-danger btn-sm delete-teacher-btn"><i class="bi bi-trash3"></i></button></td>
        `;
        tableBody.appendChild(newRow);
    }
    
    // Function to show a Bootstrap toast message
    function showToast(title, message, type = 'success') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
});