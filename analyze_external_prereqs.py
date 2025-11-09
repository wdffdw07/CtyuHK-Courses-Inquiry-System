import sqlite3
import re

conn = sqlite3.connect('outputs/courses.db')
cur = conn.cursor()

# 获取所有课程代码
cur.execute('SELECT DISTINCT course_code FROM courses')
all_courses = set(r[0] for r in cur.fetchall())

# 获取所有前置课程代码
cur.execute('SELECT DISTINCT prereq_code FROM prerequisites')
all_prereqs = set(r[0] for r in cur.fetchall())

# 找出外部前置课程
external = all_prereqs - all_courses

print(f"分析外部前置课程 (共 {len(external)} 个)\n")
print("=" * 80)

for ext_code in sorted(external):
    # 查找哪些课程需要这个外部前置
    cur.execute('SELECT course_code FROM prerequisites WHERE prereq_code = ?', (ext_code,))
    dependent_courses = [r[0] for r in cur.fetchall()]
    
    print(f"\n外部前置: {ext_code}")
    print(f"  被以下课程依赖: {', '.join(dependent_courses)}")
    
    # 对于每个依赖课程，检查它的完整前置课程列表
    for dep_course in dependent_courses:
        # 从courses表获取原始prerequisites字段
        cur.execute('SELECT course_code, course_title FROM courses WHERE course_code = ?', (dep_course,))
        course_info = cur.fetchone()
        
        if course_info:
            code, title = course_info
            
            # 获取该课程的所有前置课程
            cur.execute('SELECT prereq_code FROM prerequisites WHERE course_code = ? ORDER BY prereq_code', (dep_course,))
            all_prereq_codes = [r[0] for r in cur.fetchall()]
            
            # 区分内部和外部
            internal_prereqs = [p for p in all_prereq_codes if p in all_courses]
            external_prereqs = [p for p in all_prereq_codes if p not in all_courses]
            
            print(f"\n  → {code}: {title}")
            print(f"     内部前置课程 (在本专业中): {', '.join(internal_prereqs) if internal_prereqs else '无'}")
            print(f"     外部前置课程 (不在本专业): {', '.join(external_prereqs)}")
            
            # 判断是否为"或"的关系（通过检查课程数量）
            if len(all_prereq_codes) > 1:
                print(f"     ⚠ 注意: 有 {len(all_prereq_codes)} 个前置课程，可能是'或'的关系（二选一/多选一）")

conn.close()
