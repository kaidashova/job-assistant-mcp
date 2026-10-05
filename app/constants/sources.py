import re

DOU_FEED_URL = "https://jobs.dou.ua/vacancies/feeds/"

# DOU only supports a fixed set of categories; anything else falls back to the full feed
DOU_CATEGORIES = {
    "python": "Python",
    "java": "Java",
    "javascript": "Front End",
    "frontend": "Front End",
    "front end": "Front End",
    "react": "Front End",
    "node.js": "Node.js",
    ".net": ".NET",
    "c#": ".NET",
    "php": "PHP",
    "ruby": "Ruby",
    "golang": "Golang",
    "go": "Golang",
    "c++": "C++",
    "scala": "Scala",
    "ios": "iOS",
    "android": "Android",
    "devops": "DevOps",
    "qa": "QA",
    "data science": "Data Science",
    "machine learning": "Data Science",
    "ai": "Data Science",
    "data engineer": "Data Engineer",
    "sql": "SQL/DBA",
}

DJINNI_FEED_URL = "https://djinni.co/jobs/rss/"

DJINNI_KEYWORDS = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "JavaScript",
    "node.js": "NodeJS",
    "react": "React Native",
    "php": "PHP",
    "ruby": "Ruby",
    "go": "Golang",
    "golang": "Golang",
    "c++": "C++",
    ".net": ".NET",
    "c#": ".NET",
    "scala": "Scala",
    "devops": "DevOps",
    "qa": "QA Manual",
    "data science": "Data Science",
    "data engineer": "Data Engineer",
    "machine learning": "Data Science",
    "ai": "Data Science",
}

REMOTE_HINTS = re.compile(r"\b(remote|worldwide|anywhere|wfh)\b|віддален", re.IGNORECASE)
