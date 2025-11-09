import sqlite3

conn = sqlite3.connect('outputs/courses.db')
cursor = conn.cursor()

# 获取所有课程代码
cursor.execute('SELECT DISTINCT course_code FROM courses')
all_courses = set(r[0] for r in cursor.fetchall())

# 获取所有前置课程代码
cursor.execute('SELECT DISTINCT prereq_code FROM prerequisites')
all_prereqs = set(r[0] for r in cursor.fetchall())

# 找出外部前置课程（在prerequisites表中作为prereq，但不在courses表中）
external = all_prereqs - all_courses

print(f'Total courses in course list: {len(all_courses)}')
print(f'Total unique prerequisites: {len(all_prereqs)}')
print(f'External prerequisites (not in course list): {len(external)}')

if external:
    print('\nExternal prerequisite examples:')
    for code in sorted(external)[:20]:
        # 查找哪些课程需要这个外部前置
        cursor.execute('SELECT course_code FROM prerequisites WHERE prereq_code = ?', (code,))
        dependent_courses = [r[0] for r in cursor.fetchall()]
        print(f'  {code} -> required by: {", ".join(dependent_courses[:5])}{"..." if len(dependent_courses) > 5 else ""}')
else:
    print('\nNo external prerequisites found - all prerequisites are in the course list.')

conn.close()
