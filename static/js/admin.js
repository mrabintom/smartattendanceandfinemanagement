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

    // Show modal for adding teacher
    document.getElementById("addDummyTeacher").addEventListener("click", function() {
        var modal = new bootstrap.Modal(document.getElementById('addTeacherModal'));
        modal.show();
    });

    // Handle add teacher form submission
    document.getElementById("addTeacherForm").addEventListener("submit", function(e) {
        e.preventDefault();
        fetch("/admin/add_teacher", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                teacher_name: document.getElementById("teacherName").value,
                teacher_email: document.getElementById("teacherEmail").value,
                teacher_department: document.getElementById("teacherDepartment").value,
                teacher_password: document.getElementById("teacherPassword").value,
                teacher_status: "Active"
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || "Failed to add teacher.");
            }
        });
    });

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
            <td><button class="btn btn-danger btn-sm delete-teacher-btn" data-id="${teacher.id}"><i class="bi bi-trash3"></i></button></td>
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

    document.querySelectorAll('.delete-teacher-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (confirm("Are you sure you want to delete this teacher?")) {
                fetch(`/admin/delete_teacher/${btn.dataset.id}`, {
                    method: "POST",
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Remove the row from the table
                        btn.closest('tr').remove();
                    } else {
                        alert(data.message || "Failed to delete teacher.");
                    }
                });
            }
        });
    });

    document.getElementById("viewMoreAttendanceBtn").addEventListener("click", function() {
        const tbody = document.getElementById("attendanceTableBody");
        tbody.innerHTML = `{% for record in attendance_records %}
        <tr>
            <td>{{ record.date.strftime('%Y-%m-%d') }}</td>
            <td>{{ record.student_id }}</td>
            <td>{{ record.student_name }}</td>
            <td>{{ record.department }}</td>
            <td>
                {% if record.status == 'Late' %}
                    <span class="badge bg-warning text-dark">Late</span>
                {% elif record.status == 'Present' %}
                    <span class="badge bg-success">Present</span>
                {% else %}
                    <span class="badge bg-danger">{{ record.status }}</span>
                {% endif %}
            </td>
            <td>{{ record.time.strftime('%H:%M') if record.time else '-' }}</td>
            <td>{{ record.late_by if record.late_by else '0' }}</td>
        </tr>
        {% endfor %}`;
        this.style.display = "none";
    });
});