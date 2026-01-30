"""
Script to add CRUD modals and action buttons to attendance_list_v2.html
This adds:
1. Modal for Create/Edit attendance
2. Modal for Delete confirmation  
3. Action buttons (Edit/Delete) in each table row
4. JavaScript for handling AJAX submissions
"""

# Read the current template
with open('templates/operations/attendance_list_v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Wire the "Record Attendance" button to open modal
content = content.replace(
    "<button class='bg-brand-navy hover:bg-brand-dark text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-sm shadow-brand-navy/20'>",
    "<button onclick='openAttendanceModal()' class='bg-brand-navy hover:bg-brand-dark text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-sm shadow-brand-navy/20'>"
)

# 2. Add Actions column header in table
content = content.replace(
    "<th\n                            class='px-6 py-4 text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider text-right'>\n                            Total</th>",
    "<th\n                            class='px-6 py-4 text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider text-right'>\n                            Total</th>\n                        <th\n                            class='px-6 py-4 text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider text-center'>\n                            Actions</th>"
)

# 3. Add action buttons in table rows (before the closing </tr>)
action_buttons = """                        <!-- Actions -->
                        <td class='px-6 py-4 text-center'>
                            <div class='flex items-center justify-center gap-2'>
                                <button onclick='editAttendance({{ record.id }}, "{{ record.date|date:"Y-m-d" }}", "{{ record.service_type }}", {{ record.adult_count }}, {{ record.children_count }}, {{ record.first_timers_count }})' 
                                        class='p-1.5 text-slate-400 hover:text-brand-navy hover:bg-brand-navy/10 rounded transition-colors' title='Edit'>
                                    <i data-lucide='edit-2' class='w-4 h-4'></i>
                                </button>
                                <button onclick='confirmDelete({{ record.id }}, "{{ record.date|date:"M d, Y" }}", "{{ record.service_type }}")' 
                                        class='p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors' title='Delete'>
                                    <i data-lucide='trash-2' class='w-4 h-4'></i>
                                </button>
                            </div>
                        </td>
                    </tr>"""

content = content.replace("                    </tr>", action_buttons)

# 4. Add modals and JavaScript before {% endblock %}
modals_and_js = """
    <!-- Create/Edit Attendance Modal -->
    <div id='attendanceModal' class='hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4'>
        <div class='bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto'>
            <div class='p-6 border-b border-slate-200 dark:border-white/10'>
                <h3 id='modalTitle' class='text-xl font-bold text-slate-900 dark:text-white'>Record Attendance</h3>
            </div>
            <form id='attendanceForm' class='p-6 space-y-4'>
                <input type='hidden' id='attendanceId' name='id'>
                
                <div class='grid grid-cols-2 gap-4'>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Date *</label>
                        <input type='date' id='date' name='date' required
                               class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                    </div>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Service Type *</label>
                        <select id='service_type' name='service_type' required
                                class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                            <option value=''>Select Service</option>
                            <option value='Sunday Service'>Sunday Service</option>
                            <option value='Midweek Service'>Midweek Service</option>
                            <option value='Special Event'>Special Event</option>
                            <option value='Evening Sacrifice'>Evening Sacrifice</option>
                            <option value='Prayer Meeting'>Prayer Meeting</option>
                            <option value='Youth Service'>Youth Service</option>
                        </select>
                    </div>
                </div>

                <div class='grid grid-cols-3 gap-4'>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Adults *</label>
                        <input type='number' id='adult_count' name='adult_count' min='0' required
                               class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                    </div>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Children *</label>
                        <input type='number' id='children_count' name='children_count' min='0' required
                               class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                    </div>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>First Timers *</label>
                        <input type='number' id='first_timers_count' name='first_timers_count' min='0' required
                               class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                    </div>
                </div>

                <div class='flex justify-end gap-3 pt-4'>
                    <button type='button' onclick='closeAttendanceModal()' 
                            class='px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors'>
                        Cancel
                    </button>
                    <button type='submit' 
                            class='px-4 py-2 bg-brand-navy hover:bg-brand-dark text-white rounded-lg transition-colors'>
                        Save Attendance
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div id='deleteModal' class='hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4'>
        <div class='bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full'>
            <div class='p-6'>
                <div class='flex items-center gap-4 mb-4'>
                    <div class='p-3 bg-red-100 dark:bg-red-900/20 rounded-full'>
                        <i data-lucide='alert-triangle' class='w-6 h-6 text-red-600'></i>
                    </div>
                    <div>
                        <h3 class='text-lg font-bold text-slate-900 dark:text-white'>Delete Attendance Record</h3>
                        <p class='text-sm text-slate-500 dark:text-slate-400 mt-1'>This action cannot be undone</p>
                    </div>
                </div>
                <p id='deleteMessage' class='text-slate-600 dark:text-slate-300 mb-6'></p>
                <div class='flex justify-end gap-3'>
                    <button onclick='closeDeleteModal()' 
                            class='px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors'>
                        Cancel
                    </button>
                    <button onclick='deleteAttendance()' 
                            class='px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors'>
                        Delete
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentDeleteId = null;

        function openAttendanceModal(id = null) {
            document.getElementById('attendanceModal').classList.remove('hidden');
            document.getElementById('attendanceForm').reset();
            document.getElementById('attendanceId').value = '';
            document.getElementById('modalTitle').textContent = 'Record Attendance';
        }

        function closeAttendanceModal() {
            document.getElementById('attendanceModal').classList.add('hidden');
        }

        function editAttendance(id, date, serviceType, adults, children, firstTimers) {
            document.getElementById('attendanceId').value = id;
            document.getElementById('date').value = date;
            document.getElementById('service_type').value = serviceType;
            document.getElementById('adult_count').value = adults;
            document.getElementById('children_count').value = children;
            document.getElementById('first_timers_count').value = firstTimers;
            document.getElementById('modalTitle').textContent = 'Edit Attendance';
            document.getElementById('attendanceModal').classList.remove('hidden');
        }

        function confirmDelete(id, date, serviceType) {
            currentDeleteId = id;
            document.getElementById('deleteMessage').textContent = `Are you sure you want to delete the attendance record for ${serviceType} on ${date}?`;
            document.getElementById('deleteModal').classList.remove('hidden');
        }

        function closeDeleteModal() {
            document.getElementById('deleteModal').classList.add('hidden');
            currentDeleteId = null;
        }

        function deleteAttendance() {
            if (!currentDeleteId) return;

            fetch(`/attendance/${currentDeleteId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error deleting record');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting record');
            });
        }

        document.getElementById('attendanceForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const id = document.getElementById('attendanceId').value;
            const url = id ? `/attendance/${id}/update/` : '/attendance/create/';
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error saving record: ' + JSON.stringify(data.errors));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saving record');
            });
        });
    </script>
"""

# Insert modals before {% endblock %}
content = content.replace("{% endblock %}", modals_and_js + "\n{% endblock %}")

# Write the updated content
with open('templates/operations/attendance_list_v2.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added CRUD modals and action buttons to attendance_list_v2.html")
