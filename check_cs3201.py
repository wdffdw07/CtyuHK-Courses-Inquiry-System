import sqlite3

conn = sqlite3.connect('outputs/courses.db')
cur = conn.cursor()

# 查找 CS3201 或 C3201
cur.execute("SELECT course_code, course_title FROM courses WHERE course_code LIKE 'CS3201%' OR course_code LIKE 'C3201%'")
rows = cur.fetchall()
print('Courses matching CS3201 or C3201:')
for code, title in rows:
    print(f'  {code}: {title}')
    
    # 查找该课程的前置课程
    cur.execute("SELECT prereq_code FROM prerequisites WHERE course_code = ?", (code,))
    prereqs = cur.fetchall()
    
    if prereqs:
        print(f'  Prerequisites for {code}:')
        for (p,) in prereqs:
            # 检查这个前置课程是否在课程列表中
            cur.execute("SELECT course_code FROM courses WHERE course_code = ?", (p,))
            exists = cur.fetchone()
            if exists:
                print(f'    {p} (in course list)')
            else:
                print(f'    {p} (EXTERNAL - not in course list)')
    else:
        print(f'  No prerequisites found for {code}')
    print()

conn.close()
