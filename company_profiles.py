# company_profiles.py
# This file contains predefined skill profiles for various companies.
# Each company has a description and a list of keywords (skills)
# that are typically associated with roles at that company.

COMPANY_SKILL_PROFILES = {
    "Google": {
        "description": "A global technology company focusing on search, cloud computing, artificial intelligence, and hardware.",
        "keywords": ["Google Cloud Platform", "GCP", "Kubernetes", "TensorFlow", "Python", "Go", "Machine Learning", "BigQuery", "Data Science", "AI", "Distributed Systems", "Algorithms", "Scale", "Innovation", "Android", "Chrome", "Deep Learning", "Search Engine Optimization", "AdTech", "Material Design", "Wearables", "Autonomous Vehicles (Waymo)", "Robotics"]
    },
    "Microsoft": {
        "description": "A multinational technology corporation producing computer software, consumer electronics, personal computers, and related services.",
        "keywords": ["Azure", "C#", ".NET", "SQL Server", "Microsoft 365", "Dynamics 365", "Power BI", "Cloud Computing", "Enterprise Software", "Windows", "AI", "DevOps", "Cybersecurity", "TypeScript", "Gaming (Xbox)", "Active Directory", "SharePoint", "Visual Studio", "Low-Code (Power Apps)", "Mixed Reality (HoloLens)", "Quantum Computing"]
    },
    "Amazon": {
        "description": "An American multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence.",
        "keywords": ["AWS", "Java", "Python", "Distributed Systems", "Microservices", "Cloud Computing", "SQL", "NoSQL", "Leadership", "Problem Solving", "Serverless", "DynamoDB", "S3", "Lambda", "EC2", "E-commerce", "Logistics", "Machine Learning", "Alexa", "Data Engineering", "Supply Chain", "Retail Tech", "Fulfillment", "Prime Video", "Kindle", "Robotics (Warehouse)", "Natural Language Processing (NLP)", "Computer Vision"]
    },
    "Meta (Facebook)": {
        "description": "A technology conglomerate focusing on social media, virtual reality, and artificial intelligence.",
        "keywords": ["React", "PyTorch", "GraphQL", "AI", "Machine Learning", "Virtual Reality (VR)", "Augmented Reality (AR)", "Social Media", "Data Science", "Python", "PHP", "Distributed Systems", "Mobile Development", "Computer Vision", "Privacy", "Content Moderation", "Recommendation Engines", "AdTech", "Horizon Worlds", "Ray-Ban Meta Smart Glasses"]
    },
    "Apple": {
        "description": "A multinational technology company focusing on consumer electronics, software, and online services.",
        "keywords": ["Swift", "Objective-C", "iOS Development", "macOS Development", "User Experience (UX)", "Product Design", "Hardware Integration", "Privacy", "Security", "iOS", "Xcode", "Mobile Development", "Hardware Engineering", "Design Thinking", "AI (Siri)", "Cloud (iCloud)", "WatchOS", "iPadOS", "tvOS", "Apple Silicon", "HealthKit", "ARKit", "Apple Pay", "App Store", "Services Revenue"]
    },
    "Netflix": {
        "description": "A streaming service and production company.",
        "keywords": ["Python", "AWS", "Microservices", "Data Science", "Machine Learning", "Distributed Systems", "Streaming Technologies", "Recommendation Systems", "Cloud Computing", "Cloud Native", "DevOps", "Big Data", "User Experience (UX)", "Content Delivery Networks (CDN)", "Video Encoding", "Personalization", "A/B Testing", "Chaos Engineering"]
    },
    "Salesforce": {
        "description": "A cloud-based software company providing customer relationship management (CRM) service.",
        "keywords": ["Salesforce CRM", "Apex", "Visualforce", "Lightning Web Components", "Cloud Computing", "SaaS", "Customer Relationship Management", "JavaScript", "API Integration", "CRM", "Integration (MuleSoft)", "Platform Development", "Marketing Cloud", "Service Cloud", "Einstein AI", "Tableau", "Slack"]
    },
    "IBM": {
        "description": "An American multinational technology and consulting company, specializing in computer hardware, middleware, and software.",
        "keywords": ["Java", "Python", "Cloud Computing", "AI", "Machine Learning", "Data Science", "Blockchain", "Cybersecurity", "Enterprise Software", "Consulting", "Cloud Computing (IBM Cloud)", "AI (Watson)", "Enterprise Solutions", "Quantum Computing", "Hybrid Cloud", "Data Analytics", "Linux", "Mainframe", "Red Hat", "OpenShift", "Automation (RPA)", "IT Services", "Storage Solutions", "Server Technologies"]
    },
    "Oracle": {
        "description": "A multinational computer technology corporation best known for its database software and cloud engineered systems.",
        "keywords": ["Java", "SQL", "Oracle Database", "Cloud Computing", "Enterprise Software", "ERP", "CRM", "Data Warehousing", "Middleware", "Cloud Infrastructure (OCI)", "Fusion Applications", "NetSuite", "Peoplesoft", "Supply Chain Management"]
    },
    "Accenture": {
        "description": "A leading global professional services company, providing a broad range of services and solutions in strategy, consulting, digital, technology and operations.",
        "keywords": ["Consulting", "Project Management", "Change Management", "Digital Transformation", "Cloud Computing", "Data Analytics", "Strategy", "Business Process Improvement", "IT Strategy", "System Integration", "Enterprise Architecture", "Cybersecurity Consulting", "AI Consulting", "Blockchain Consulting"]
    },
    "Tata Consultancy Services (TCS)": {
        "description": "A leading global IT services, consulting, and business solutions organization and part of the Tata Group.",
        "keywords": ["IT Services", "Consulting", "Digital Transformation", "Cloud Computing", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Cybersecurity", "IoT", "Agile", "DevOps", "Java", "Python", "SAP", "Oracle", "Automation", "Blockchain", "Financial Services", "Manufacturing", "Cognitive Business Operations", "Assurance Services", "Engineering & Industrial Services"]
    },
    "Infosys": {
        "description": "A global leader in next-generation digital services and consulting.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "IoT", "Automation", "Enterprise Applications", "SAP", "Oracle", "Java", "Python", "Big Data", "DevOps", "Blockchain", "Consulting", "Digital Experience", "Legacy Modernization", "Finacle (Banking Software)"]
    },
    "Wipro": {
        "description": "A global information technology, consulting, and business process services company.",
        "keywords": ["IT Services", "Consulting", "Digital Transformation", "Cloud Computing", "AI", "Machine Learning", "Data Science", "Cybersecurity", "IoT", "Automation", "DevOps", "SAP", "Oracle", "Java", "Python", "Analytics", "Blockchain", "Industry Solutions", "Application Development & Management", "Infrastructure Services"]
    },
    "HCLTech": {
        "description": "A global technology company that helps enterprises reimagine their businesses for the digital age.",
        "keywords": ["Digital Engineering", "Cloud Adoption", "IoT Solutions", "Automation", "Security", "Analytics", "Digital Transformation", "AI", "Machine Learning", "Cybersecurity", "Fullstack Development", "Cloud Native", "DevOps", "Enterprise Applications", "Product Engineering", "Infrastructure Modernization"]
    },
    "Capgemini": {
        "description": "A global leader in consulting, technology services, and digital transformation.",
        "keywords": ["Consulting", "IT Services", "Digital Transformation", "Cloud Computing", "AI", "Data Analytics", "Cybersecurity", "Application Services", "DevOps", "Agile", "SAP", "Oracle", "Industry Expertise", "Intelligent Automation", "Customer Experience"]
    },
    "Cognizant": {
        "description": "A global information technology services and consulting company.",
        "keywords": ["IT Consulting", "Digital Strategy", "Cloud Solutions", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "Application Development", "Business Process Services", "Industry Solutions", "DevOps", "Agile", "Digital Engineering", "Enterprise Transformation"]
    },
    "Tech Mahindra": {
        "description": "An Indian multinational information technology services and consulting company.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Cybersecurity", "Network Services", "Business Process Services", "Enterprise Applications", "Engineering Services", "Blockchain", "5G", "IoT", "Robotics", "Telecommunications", "CRM Services", "Data Analytics"]
    },
    "LTIMindtree": {
        "description": "An Indian multinational information technology services and consulting company, formed by the merger of L&T Infotech and Mindtree.",
        "keywords": ["IT Services", "Digital Transformation", "Cloud Computing", "Data & Analytics", "Generative AI", "Application Development", "Cybersecurity", "Enterprise Solutions", "IoT", "DevOps", "Agile", "Consulting", "Product Engineering", "Customer Experience (CX)", "SAP", "Oracle"]
    },
    "Persistent Systems": {
        "description": "A global services company that provides software product development and technology services.",
        "keywords": ["Product Engineering", "Digital Engineering", "Cloud Native", "Data & AI", "Enterprise Modernization", "Software Development", "Agile", "DevOps", "Banking & Financial Services (BFS)", "Healthcare Tech", "Life Sciences", "IoT Solutions"]
    },
    "Mphasis": {
        "description": "A global information technology solutions provider specializing in cloud and cognitive services.",
        "keywords": ["Cloud Transformation", "AI", "Cognitive Technologies", "Digital Transformation", "DevOps", "Automation", "Cybersecurity", "Data Analytics", "IT Services", "Blockchain", "Application Modernization", "Financial Services Tech"]
    },
    "Coforge": {
        "description": "A global IT solutions organization enabling businesses to transform with digital technologies.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Automation", "Cybersecurity", "Application Development", "Microservices", "API Management", "Travel Tech", "Financial Services"]
    },
    "Zensar Technologies": {
        "description": "A global technology services company, providing digital solutions and technology consulting.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "Enterprise Applications", "DevOps", "Agile", "Robotics Process Automation (RPA)"]
    },
    "Cyient": {
        "description": "A global engineering and technology solutions company.",
        "keywords": ["Engineering Services", "Geospatial", "IoT", "Data Analytics", "Aerospace", "Automotive", "Medical Devices", "Manufacturing", "Digital Engineering", "Product Design"]
    },
    "L&T Technology Services": {
        "description": "A global pure-play engineering research and development services company.",
        "keywords": ["Engineering Services", "Digital Engineering", "IoT", "AI", "Machine Learning", "Embedded Systems", "Automotive", "Aerospace", "Medical Devices", "Manufacturing Automation", "Product Development"]
    },
    "Firstsource Solutions": {
        "description": "A global provider of business process management (BPM) services.",
        "keywords": ["Customer Experience", "Business Process Management", "Digital Transformation", "Data Analytics", "Healthcare BPO", "Financial Services BPO", "Telecom BPO", "Robotics Process Automation (RPA)", "AI in CX"]
    },
    "ExlService Holdings": {
        "description": "A global analytics and digital operations and solutions company.",
        "keywords": ["Data Analytics", "AI", "Machine Learning", "Digital Transformation", "Operations Management", "Finance & Accounting BPO", "Healthcare Analytics", "Insurance Analytics", "Business Process Optimization"]
    },
    "Genpact": {
        "description": "A global professional services firm focused on delivering digital transformation and business process management.",
        "keywords": ["Digital Transformation", "Business Process Management (BPM)", "AI & Automation", "Data Analytics", "Financial Services Operations", "Supply Chain Management", "Risk & Compliance", "Robotics Process Automation (RPA)", "Consulting"]
    },
    "Concentrix": {
        "description": "A global provider of customer experience (CX) solutions and technology.",
        "keywords": ["Customer Experience", "Business Process Management", "Digital Transformation", "Contact Center", "CX Consulting", "Sales", "Marketing", "AI in CX", "Automation"]
    },
    "Teleperformance": {
        "description": "A global leader in omnichannel customer experience management.",
        "keywords": ["Customer Experience", "Omnichannel Solutions", "Digital Transformation", "Contact Center", "Business Process Outsourcing", "AI in CX", "Customer Support"]
    },
    "Conduent": {
        "description": "A global business process services company.",
        "keywords": ["Business Process Solutions", "Digital Platforms", "Healthcare BPS", "Transportation Solutions", "Government Services", "Commercial Industries", "Payment Solutions", "HR Services"]
    },
    "Sutherland": {
        "description": "A global process transformation company.",
        "keywords": ["Digital Transformation", "Customer Experience", "Business Process Transformation", "AI", "Automation", "Healthcare BPS", "Financial Services BPS", "Retail BPS", "Robotics Process Automation (RPA)"]
    },
    "Startek": {
        "description": "A global provider of customer experience management solutions.",
        "keywords": ["Customer Experience", "Omnichannel Solutions", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "Transcom": {
        "description": "A global customer experience specialist.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "Alorica": {
        "description": "A global leader in customer experience solutions.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "TTEC": {
        "description": "A global customer experience technology and services company.",
        "keywords": ["Customer Experience", "Digital Transformation", "Contact Center", "AI", "Automation", "Consulting", "Customer Engagement"]
    },
    "VXI Global Solutions": {
        "description": "A global leader in customer care and customer experience (CX) solutions.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "Sitel Group": {
        "description": "A global leader in customer experience products and solutions.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "TaskUs": {
        "description": "A leading provider of digital customer experience, content security, and AI operations.",
        "keywords": ["Digital Customer Experience", "Content Moderation", "AI Operations", "Gaming Support", "Fintech Support", "E-commerce Support", "Trust & Safety"]
    },
    "Arise Virtual Solutions": {
        "description": "A leading platform for crowdsourced customer service.",
        "keywords": ["Virtual Contact Center", "Customer Service", "Sales", "Technical Support", "Work-from-Home Solutions", "Gig Economy"]
    },
    "LiveOps": {
        "description": "A cloud contact center platform for remote agents.",
        "keywords": ["Cloud Contact Center", "Customer Service", "Sales", "Technical Support", "Work-from-Home Solutions", "Remote Operations"]
    },
    "Modis": {
        "description": "A global leader in professional solutions, specializing in IT and engineering.",
        "keywords": ["IT Consulting", "Digital Transformation", "Talent Solutions", "Cloud", "Cybersecurity", "Data & AI", "Engineering Services"]
    },
    "TEKsystems": {
        "description": "A leading provider of IT staffing solutions, IT services and talent management expertise.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Management"]
    },
    "Insight Global": {
        "description": "A national staffing and services company.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Robert Half Technology": {
        "description": "A leading provider of IT professionals on a contract, contract-to-hire and permanent basis.",
        "keywords": ["IT Staffing", "IT Consulting", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Acquisition"]
    },
    "Kforce": {
        "description": "A professional staffing and solutions firm specializing in Technology and Finance & Accounting.",
        "keywords": ["IT Staffing", "IT Consulting", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Finance & Accounting Staffing"]
    },
    "Apex Systems": {
        "description": "A leading IT staffing and services firm.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Collabera": {
        "description": "A global IT staffing and services company.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Hays": {
        "description": "A leading global professional recruiting group.",
        "keywords": ["IT Staffing", "IT Recruitment", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Acquisition"]
    },
    "Michael Page": {
        "description": "A leading professional recruitment consultancy specializing in IT.",
        "keywords": ["IT Recruitment", "IT Staffing", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Acquisition"]
    },
    "Randstad Technologies": {
        "description": "A leading provider of IT talent and solutions.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Adecco": {
        "description": "A global leader in human resource solutions.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "HR Solutions"]
    },
    "Kelly Services": {
        "description": "A global leader in providing workforce solutions.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Workforce Solutions"]
    },
    "ManpowerGroup": {
        "description": "A global workforce solutions company.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Workforce Solutions"]
    },
    "Aerotek": {
        "description": "A leading recruiting and staffing agency.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Staffing Solutions"]
    },
    "CDW": {
        "description": "A leading provider of technology solutions to business, government, education and healthcare.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Hardware", "Software"]
    },
    "Insight Enterprises": {
        "description": "A Fortune 500 global technology provider of hardware, software, cloud, and service solutions.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Digital Transformation"]
    },
    "Presidio": {
        "description": "A global digital services and solutions provider.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Digital Transformation"]
    },
    "ePlus": {
        "description": "A leading provider of technology solutions.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Digital Transformation"]
    },
    "Optiv": {
        "description": "A leading cybersecurity solutions and services company.",
        "keywords": ["Cybersecurity Solutions", "Security Consulting", "Managed Security Services", "Identity & Access Management", "Cloud Security", "Security Operations"]
    },
    "Herjavec Group": {
        "description": "A global cybersecurity advisory firm and managed security services provider.",
        "keywords": ["Cybersecurity Solutions", "Security Consulting", "Managed Security Services", "Identity & Access Management", "Cloud Security", "Incident Response"]
    },
    "Rapid7": {
        "description": "A leading provider of security analytics and automation.",
        "keywords": ["Vulnerability Management", "Security Operations", "Application Security", "Cloud Security", "Threat Intelligence", "Incident Response"]
    },
    "Tenable": {
        "description": "A leading provider of Cyber Exposure solutions.",
        "keywords": ["Vulnerability Management", "Cyber Exposure", "OT Security", "Cloud Security", "Web Application Security", "Attack Surface Management"]
    },
    "Qualys": {
        "description": "A pioneer and leading provider of cloud-based security and compliance solutions.",
        "keywords": ["Vulnerability Management", "Cloud Security", "Web Application Security", "Compliance", "Asset Management", "Security Audits"]
    },
    "CrowdStrike": {
        "description": "A leader in cloud-native endpoint protection.",
        "keywords": ["Endpoint Security", "Cloud Security", "Threat Intelligence", "Incident Response", "Managed Detection and Response (MDR)", "XDR"]
    },
    "SentinelOne": {
        "description": "A leading provider of AI-powered endpoint security.",
        "keywords": ["Endpoint Security", "Cloud Security", "Threat Intelligence", "Incident Response", "XDR", "AI in Security"]
    },
    "Palo Alto Networks": {
        "description": "A global cybersecurity leader.",
        "keywords": ["Network Security", "Cloud Security", "Endpoint Security", "Security Operations", "Threat Prevention", "Firewalls", "AI in Security"]
    },
    "Fortinet": {
        "description": "A global leader in broad, integrated, and automated cybersecurity solutions.",
        "keywords": ["Network Security", "Cloud Security", "Endpoint Security", "Security Operations", "Threat Prevention", "Firewalls", "SD-WAN"]
    },
    "Cisco": {
        "description": "An American multinational digital communications technology conglomerate corporation.",
        "keywords": ["Networking", "Cybersecurity", "Collaboration", "Cloud", "Data Center", "IoT", "Routers", "Switches", "Webex", "Meraki"]
    },
    "Juniper Networks": {
        "description": "A global leader in networking innovations.",
        "keywords": ["Networking", "Cloud", "AI-driven Enterprise", "Security", "Automation", "Routers", "Switches", "SD-WAN"]
    },
    "VMware": {
        "description": "A cloud computing and virtualization technology company, now part of Broadcom.",
        "keywords": ["Virtualization", "Cloud Computing", "Network Virtualization", "Security", "Digital Workspace", "SDDC", "NSX", "vSAN", "Tanzu", "Kubernetes"]
    },
    "Citrix": {
        "description": "A company providing digital workspace, networking, and analytics solutions.",
        "keywords": ["Virtualization", "Cloud Computing", "Digital Workspace", "Networking", "Security", "VDI", "Application Delivery"]
    },
    "Red Hat": {
        "description": "A leading provider of open source software solutions.",
        "keywords": ["Open Source", "Linux", "Cloud Computing", "Kubernetes", "Automation", "Middleware", "DevOps", "OpenShift", "Ansible"]
    },
    "SUSE": {
        "description": "A global leader in open source software, specializing in Linux, Kubernetes, and Edge solutions.",
        "keywords": ["Open Source", "Linux", "Kubernetes", "Cloud Computing", "Edge Computing", "Storage", "Rancher"]
    },
    "Canonical (Ubuntu)": {
        "description": "The company behind Ubuntu, a popular open-source operating system.",
        "keywords": ["Open Source", "Linux", "Cloud Computing", "IoT", "AI/ML", "Containers", "Ubuntu", "Kubernetes"]
    },
    "MongoDB": {
        "description": "A leading NoSQL database provider.",
        "keywords": ["NoSQL Database", "Document Database", "Cloud Database", "Atlas", "Enterprise Advanced", "Data Modeling (NoSQL)"]
    },
    "Databricks": {
        "description": "A company providing a cloud-based data lakehouse platform for data science and AI.",
        "keywords": ["Data Lakehouse", "Spark", "AI/ML", "Data Engineering", "Data Science", "Delta Lake", "MLflow", "Lakehouse Architecture", "Python", "Scala", "SQL"]
    },
    "Snowflake": {
        "description": "A cloud-based data warehousing company offering a data cloud platform.",
        "keywords": ["Cloud Data Warehouse", "Data Lake", "Data Sharing", "Data Marketplace", "Data Applications", "SQL", "Data Governance"]
    },
    "Teradata": {
        "description": "A leading provider of pervasive data intelligence.",
        "keywords": ["Enterprise Data Warehouse", "Cloud Data Analytics", "Hybrid Cloud", "AI/ML Integration", "Data Management"]
    },
    "Cloudera": {
        "description": "A hybrid data cloud company.",
        "keywords": ["Data Cloud", "Data Management", "Data Analytics", "Machine Learning", "Hybrid Cloud", "Open Source", "Hadoop", "Spark"]
    },
    "Confluent": {
        "description": "A company providing an event streaming platform based on Apache Kafka.",
        "keywords": ["Kafka", "Event Streaming Platform", "Data in Motion", "Cloud-Native", "Real-Time Data", "Apache Kafka"]
    },
    "Elastic (Elasticsearch)": {
        "description": "A company behind the Elastic Stack (Elasticsearch, Kibana, Logstash, Beats).",
        "keywords": ["Search Engine", "Analytics Engine", "Observability", "Security", "Elastic Stack", "Kibana", "Logstash", "Elasticsearch"]
    },
    "Redis Labs": {
        "description": "A company providing Redis Enterprise, an in-memory database platform.",
        "keywords": ["In-Memory Database", "NoSQL", "Caching", "Real-Time Data", "Redis Enterprise", "Redis"]
    },
    "Neo4j": {
        "description": "A leading graph database platform.",
        "keywords": ["Graph Database", "Graph Analytics", "Knowledge Graphs", "AI/ML", "Cypher"]
    },
    "InfluxData (InfluxDB)": {
        "description": "A company providing InfluxDB, a time series database.",
        "keywords": ["Time Series Database", "IoT", "Monitoring", "Analytics", "Cloud-Native", "InfluxDB"]
    },
    "Timescale (TimescaleDB)": {
        "description": "A company providing TimescaleDB, a PostgreSQL extension for time series data.",
        "keywords": ["Time Series Database", "PostgreSQL Extension", "IoT", "Analytics", "Cloud-Native", "TimescaleDB"]
    },
    "Vertica": {
        "description": "A columnar database for analytics.",
        "keywords": ["Columnar Database", "Analytics Database", "Data Warehousing", "Big Data Analytics"]
    },
    "ClickHouse": {
        "description": "An open-source columnar database for analytical queries.",
        "keywords": ["Columnar Database", "Analytics Database", "Real-Time Analytics", "Big Data"]
    },
    "Pinecone": {
        "description": "A vector database for AI applications.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"]
    },
    "Weaviate": {
        "description": "An open-source vector database.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Knowledge Graphs", "Semantic Search"]
    },
    "Milvus": {
        "description": "An open-source vector database for AI applications.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Similarity Search"]
    },
    "Qdrant": {
        "description": "A vector similarity search engine.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"]
    },
    "Chroma": {
        "description": "An open-source AI-native embedding database.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"]
    },
    "Faiss": {
        "description": "A library for efficient similarity search and clustering of dense vectors.",
        "keywords": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"]
    },
    "Annoy": {
        "description": "A C++ library with Python bindings for approximate nearest neighbors.",
        "keywords": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"]
    },
    "Hnswlib": {
        "description": "A C++ library for approximate nearest neighbor search.",
        "keywords": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"]
    },
    "Scikit-learn": {
        "description": "A free software machine learning library for the Python programming language.",
        "keywords": ["Machine Learning Library", "Python", "Classification", "Regression", "Clustering"]
    },
    "TensorFlow": {
        "description": "An open-source machine learning framework developed by Google.",
        "keywords": ["Deep Learning Framework", "AI/ML", "Neural Networks", "Google"]
    },
    "PyTorch": {
        "description": "An open-source machine learning library developed by Facebook AI Research.",
        "keywords": ["Deep Learning Framework", "AI/ML", "Neural Networks", "Facebook AI"]
    },
    "Keras": {
        "description": "An open-source software library that provides a Python interface for artificial neural networks.",
        "keywords": ["Deep Learning API", "TensorFlow", "Neural Networks", "Rapid Prototyping"]
    },
    "XGBoost": {
        "description": "An optimized distributed gradient boosting library.",
        "keywords": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"]
    },
    "LightGBM": {
        "description": "A gradient boosting framework that uses tree-based learning algorithms.",
        "keywords": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"]
    },
    "CatBoost": {
        "description": "An open-source gradient boosting library developed by Yandex.",
        "keywords": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"]
    },
    "Statsmodels": {
        "description": "A Python module that provides classes and functions for the estimation of many different statistical models.",
        "keywords": ["Statistical Modeling", "Econometrics", "Python", "Statistical Tests"]
    },
    "NumPy": {
        "description": "A fundamental package for scientific computing with Python.",
        "keywords": ["Numerical Computing", "Python", "Arrays", "Matrices"]
    },
    "Pandas": {
        "description": "A software library written for the Python programming language for data manipulation and analysis.",
        "keywords": ["Data Manipulation", "Data Analysis", "Python", "DataFrames"]
    },
    "Matplotlib": {
        "description": "A plotting library for the Python programming language.",
        "keywords": ["Data Visualization", "Python", "Plotting"]
    },
    "Seaborn": {
        "description": "A Python data visualization library based on matplotlib.",
        "keywords": ["Statistical Data Visualization", "Python", "Matplotlib"]
    },
    "Plotly": {
        "description": "A graphing library for Python, R, and JavaScript.",
        "keywords": ["Interactive Data Visualization", "Web-based", "Dashboards"]
    },
    "Bokeh": {
        "description": "An interactive visualization library for modern web browsers.",
        "keywords": ["Interactive Data Visualization", "Web-based", "Python"]
    },
    "Dash": {
        "description": "A Python framework for building analytical web applications.",
        "keywords": ["Web Application Framework", "Python", "Plotly"]
    },
    "Flask": {
        "description": "A micro web framework for Python.",
        "keywords": ["Web Framework", "Python", "Microframework"]
    },
    "Django": {
        "description": "A high-level Python Web framework that encourages rapid development and clean, pragmatic design.",
        "keywords": ["Web Framework", "Python", "Full-stack"]
    },
    "FastAPI": {
        "description": "A modern, fast (high-performance) web framework for building APIs with Python.",
        "keywords": ["Web Framework", "Python", "High Performance", "API Development"]
    },
    "Spring Boot": {
        "description": "An open-source, microservice-based Java web framework.",
        "keywords": ["Java Framework", "Microservices", "Web Applications"]
    },
    ".NET Core": {
        "description": "A free, cross-platform, open-source managed computer software framework.",
        "keywords": ["Cross-platform Framework", "C#", "Web Applications", "APIs"]
    },
    "Node.js": {
        "description": "A JavaScript runtime built on Chrome's V8 JavaScript engine.",
        "keywords": ["JavaScript Runtime", "Backend Development", "Server-side"]
    },
    "Express.js": {
        "description": "A minimal and flexible Node.js web application framework.",
        "keywords": ["Node.js Web Framework", "Backend Development", "APIs"]
    },
    "React": {
        "description": "A JavaScript library for building user interfaces.",
        "keywords": ["JavaScript Library", "Frontend Development", "UI Components"]
    },
    "Angular": {
        "description": "A TypeScript-based open-source web application framework.",
        "keywords": ["JavaScript Framework", "Frontend Development", "Single-page Applications"]
    },
    "Vue.js": {
        "description": "An open-source Model-View-ViewModel JavaScript framework for building user interfaces and single-page applications.",
        "keywords": ["JavaScript Framework", "Frontend Development", "Progressive Web Apps"]
    },
    "Svelte": {
        "description": "A free, open-source JavaScript framework.",
        "keywords": ["JavaScript Framework", "Frontend Development", "Component Compiler"]
    },
    "jQuery": {
        "description": "A fast, small, and feature-rich JavaScript library.",
        "keywords": ["JavaScript Library", "DOM Manipulation", "Event Handling"]
    },
    "Bootstrap": {
        "description": "A free and open-source CSS framework directed at responsive, mobile-first front-end web development.",
        "keywords": ["CSS Framework", "Responsive Design", "UI Components"]
    },
    "Tailwind CSS": {
        "description": "A utility-first CSS framework for rapidly building custom user interfaces.",
        "keywords": ["CSS Framework", "Utility-first", "Rapid UI Development"]
    },
    "Sass": {
        "description": "A preprocessor scripting language that is interpreted or compiled into CSS.",
        "keywords": ["CSS Preprocessor", "CSS Extensions"]
    },
    "Less": {
        "description": "A dynamic stylesheet language that extends CSS.",
        "keywords": ["CSS Preprocessor", "CSS Extensions"]
    },
    "Webpack": {
        "description": "A static module bundler for modern JavaScript applications.",
        "keywords": ["Module Bundler", "JavaScript Applications"]
    },
    "Babel": {
        "description": "A free and open-source JavaScript transpiler.",
        "keywords": ["JavaScript Compiler", "Transpiler"]
    },
    "npm": {
        "description": "The default package manager for the JavaScript runtime environment Node.js.",
        "keywords": ["Node Package Manager", "JavaScript Packages"]
    },
    "Yarn": {
        "description": "A fast, reliable, and secure dependency management tool.",
        "keywords": ["Package Manager", "JavaScript Packages"]
    },
    "Ansible": {
        "description": "An open-source software provisioning, configuration management, and application-deployment tool.",
        "keywords": ["Automation Engine", "IT Automation", "Configuration Management"]
    },
    "Terraform": {
        "description": "An open-source infrastructure as code software tool.",
        "keywords": ["Infrastructure as Code", "Cloud Provisioning", "Multi-cloud"]
    },
    "Jenkins": {
        "description": "An open-source automation server.",
        "keywords": ["CI/CD", "Automation Server", "Build Automation"]
    },
    "GitLab CI/CD": {
        "description": "A part of GitLab that allows for continuous integration, delivery, and deployment.",
        "keywords": ["CI/CD", "GitLab Integration", "DevOps Platform"]
    },
    "GitHub Actions": {
        "description": "A CI/CD platform that allows you to automate your build, test, and deployment pipeline.",
        "keywords": ["CI/CD", "GitHub Integration", "Workflow Automation"]
    },
    "AWS CodeBuild": {
        "description": "A fully managed continuous integration service that compiles source code, runs tests, and produces software packages that are ready to deploy.",
        "keywords": ["CI/CD", "Build Service", "AWS"]
    },
    "AWS CodePipeline": {
        "description": "A fully managed continuous delivery service that helps you automate your release pipelines.",
        "keywords": ["CI/CD", "Release Automation", "AWS"]
    },
    "AWS CodeDeploy": {
        "description": "A service that automates code deployments to any instance, including Amazon EC2 instances and on-premises servers.",
        "keywords": ["Deployment Service", "Automated Deployments", "AWS"]
    },
    "AWS Lambda": {
        "description": "A serverless, event-driven compute service.",
        "keywords": ["Serverless Computing", "Function as a Service", "AWS"]
    },
    "Azure Functions": {
        "description": "A serverless compute service that enables you to run small pieces of code.",
        "keywords": ["Serverless Computing", "Function as a Service", "Azure"]
    },
    "Google Cloud Functions": {
        "description": "A serverless execution environment for building and connecting cloud services.",
        "keywords": ["Serverless Computing", "Function as a Service", "GCP"]
    },
    "Serverless Framework": {
        "description": "An open-source web framework written in Node.js.",
        "keywords": ["Serverless Applications", "Deployment Tool"]
    },
    "Microservices": {
        "description": "A software architecture style in which complex applications are composed of small, independent processes communicating with each other using language-agnostic APIs.",
        "keywords": ["Software Architecture", "Distributed Systems"]
    },
    "API Gateway": {
        "description": "A management service for APIs.",
        "keywords": ["API Management", "API Security", "Traffic Management"]
    },
    "Service Mesh": {
        "description": "A configurable infrastructure layer for microservices applications.",
        "keywords": ["Microservices Communication", "Traffic Management", "Observability"]
    },
    "Istio": {
        "description": "An open-source service mesh that layers transparently on existing distributed applications.",
        "keywords": ["Service Mesh", "Kubernetes", "Traffic Management"]
    },
    "Linkerd": {
        "description": "An ultralight, security-first service mesh for Kubernetes.",
        "keywords": ["Service Mesh", "Kubernetes", "Traffic Management"]
    },
    "gRPC": {
        "description": "A modern open-source high-performance RPC framework.",
        "keywords": ["Remote Procedure Call", "High Performance", "Microservices"]
    },
    "RESTful APIs": {
        "description": "An architectural style for an application program interface (API) that uses HTTP requests to access and use data.",
        "keywords": ["API Design", "Web Services"]
    },
    "SOAP": {
        "description": "A messaging protocol specification for exchanging structured information in the implementation of web services.",
        "keywords": ["Web Services Protocol", "XML-based"]
    },
    "Message Queues": {
        "description": "A form of asynchronous service-to-service communication used in serverless and microservices architectures.",
        "keywords": ["Asynchronous Communication", "Decoupling Services"]
    },
    "RabbitMQ": {
        "description": "The most widely deployed open source message broker.",
        "keywords": ["Message Broker", "AMQP"]
    },
    "ActiveMQ": {
        "description": "A popular open-source, multi-protocol message broker.",
        "keywords": ["Message Broker", "JMS"]
    },
    "Kafka": {
        "description": "A distributed streaming platform.",
        "keywords": ["Distributed Streaming Platform", "Event Streaming"]
    },
    "Amazon SQS": {
        "description": "A fully managed message queuing service.",
        "keywords": ["Message Queuing Service", "AWS"]
    },
    "Amazon SNS": {
        "description": "A fully managed messaging service for both application-to-application (A2A) and application-to-person (A2P) communication.",
        "keywords": ["Notification Service", "AWS"]
    },
    "Google Cloud Pub/Sub": {
        "description": "An asynchronous messaging service that decouples senders and receivers.",
        "keywords": ["Messaging Service", "GCP"]
    },
    "Version Control": {
        "description": "A system that records changes to a file or set of files over time so that you can recall specific versions later.",
        "keywords": ["Source Code Management", "Collaboration"]
    },
    "SVN": {
        "description": "A software versioning and revision control system.",
        "keywords": ["Version Control System", "Centralized"]
    },
    "Perforce": {
        "description": "A software company that provides enterprise-scale development tools.",
        "keywords": ["Version Control System", "Enterprise"]
    },
    "Trello": {
        "description": "A web-based Kanban-style list-making application.",
        "keywords": ["Project Management Tool", "Kanban Board"]
    },
    "Asana": {
        "description": "A web and mobile application designed to help teams organize, track, and manage their work.",
        "keywords": ["Project Management Tool", "Task Management"]
    },
    "Monday.com": {
        "description": "A work operating system (Work OS) that powers teams to run projects and workflows with confidence.",
        "keywords": ["Work OS", "Project Management", "Team Collaboration"]
    },
    "Smartsheet": {
        "description": "A software as a service (SaaS) offering for collaboration and work management.",
        "keywords": ["Work Management", "Collaboration", "Project Management"]
    },
    "MS Project": {
        "description": "A project management software program developed and sold by Microsoft.",
        "keywords": ["Project Management Software", "Gantt Charts"]
    },
    "Primavera P6": {
        "description": "A project portfolio management (PPM) software.",
        "keywords": ["Project Management Software", "Enterprise Project Portfolio Management"]
    },
    "Zendesk": {
        "description": "A customer service software company.",
        "keywords": ["Customer Service Software", "Ticketing System"]
    },
    "Freshdesk": {
        "description": "A cloud-based customer service software.",
        "keywords": ["Customer Service Software", "Ticketing System"]
    },
    "ITIL": {
        "description": "A framework for IT service management.",
        "keywords": ["IT Service Management", "Framework"]
    },
    "COBIT": {
        "description": "A framework for IT governance and management.",
        "keywords": ["IT Governance", "Framework"]
    },
    "PRINCE2": {
        "description": "A structured project management methodology.",
        "keywords": ["Project Management Methodology"]
    },
    "PMP": {
        "description": "Project Management Professional certification.",
        "keywords": ["Project Management Professional", "Certification"]
    },
    "CSM": {
        "description": "Certified ScrumMaster certification.",
        "keywords": ["Certified ScrumMaster", "Certification"]
    },
    "Lean Six Sigma": {
        "description": "A methodology that relies on a collaborative team effort to improve performance by systematically removing waste and reducing variation.",
        "keywords": ["Process Improvement Methodology"]
    },
    "CFA": {
        "description": "Chartered Financial Analyst designation.",
        "keywords": ["Chartered Financial Analyst", "Certification"]
    },
    "CPA": {
        "description": "Certified Public Accountant license.",
        "keywords": ["Certified Public Accountant", "Certification"]
    },
    "SHRM-CP": {
        "description": "SHRM Certified Professional certification.",
        "keywords": ["SHRM Certified Professional", "HR Certification"]
    },
    "PHR": {
        "description": "Professional in Human Resources certification.",
        "keywords": ["Professional in Human Resources", "HR Certification"]
    },
    "CEH": {
        "description": "Certified Ethical Hacker certification.",
        "keywords": ["Certified Ethical Hacker", "Cybersecurity Certification"]
    },
    "OSCP": {
        "description": "Offensive Security Certified Professional certification.",
        "keywords": ["Offensive Security Certified Professional", "Cybersecurity Certification"]
    },
    "CCNA": {
        "description": "Cisco Certified Network Associate certification.",
        "keywords": ["Cisco Certified Network Associate", "Networking Certification"]
    },
    "CISSP": {
        "description": "Certified Information Systems Security Professional certification.",
        "keywords": ["Certified Information Systems Security Professional", "Cybersecurity Certification"]
    },
    "CISM": {
        "description": "Certified Information Security Manager certification.",
        "keywords": ["Certified Information Security Manager", "Cybersecurity Certification"]
    },
    "CompTIA Security+": {
        "description": "CompTIA Security+ certification.",
        "keywords": ["Cybersecurity Certification"]
    },
    "Google": {
        "description": "A global technology company focusing on search, cloud computing, artificial intelligence, and hardware.",
        "keywords": ["Google Cloud Platform", "GCP", "Kubernetes", "TensorFlow", "Python", "Go", "Machine Learning", "BigQuery", "Data Science", "AI", "Distributed Systems", "Algorithms", "Scale", "Innovation", "Android", "Chrome", "Deep Learning", "Search Engine Optimization", "AdTech", "Material Design", "Wearables", "Autonomous Vehicles (Waymo)", "Robotics"]
    },
    "Microsoft": {
        "description": "A multinational technology corporation producing computer software, consumer electronics, personal computers, and related services.",
        "keywords": ["Azure", "C#", ".NET", "SQL Server", "Microsoft 365", "Dynamics 365", "Power BI", "Cloud Computing", "Enterprise Software", "Windows", "AI", "DevOps", "Cybersecurity", "TypeScript", "Gaming (Xbox)", "Active Directory", "SharePoint", "Visual Studio", "Low-Code (Power Apps)", "Mixed Reality (HoloLens)", "Quantum Computing"]
    },
    "Amazon": {
        "description": "An American multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence.",
        "keywords": ["AWS", "Cloud Computing", "Serverless", "DynamoDB", "S3", "Lambda", "EC2", "Microservices", "Scale", "E-commerce", "Logistics", "Machine Learning", "Alexa", "Data Engineering", "Supply Chain", "Retail Tech", "Fulfillment", "Prime Video", "Kindle", "Robotics (Warehouse)", "Natural Language Processing (NLP)", "Computer Vision"]
    },
    "Meta (Facebook)": {
        "description": "A technology conglomerate focusing on social media, virtual reality, and artificial intelligence.",
        "keywords": ["React", "PyTorch", "GraphQL", "AI", "Machine Learning", "Virtual Reality (VR)", "Augmented Reality (AR)", "Social Media", "Data Science", "Python", "PHP", "Distributed Systems", "Mobile Development", "Computer Vision", "Privacy", "Content Moderation", "Recommendation Engines", "AdTech", "Horizon Worlds", "Ray-Ban Meta Smart Glasses"]
    },
    "Apple": {
        "description": "A multinational technology company focusing on consumer electronics, software, and online services.",
        "keywords": ["iOS", "Swift", "Objective-C", "macOS", "Xcode", "Mobile Development", "Hardware Engineering", "User Experience (UX)", "Design Thinking", "Privacy", "Security", "AI (Siri)", "Cloud (iCloud)", "WatchOS", "iPadOS", "tvOS", "Apple Silicon", "HealthKit", "ARKit", "Apple Pay", "App Store", "Services Revenue"]
    },
    "Netflix": {
        "description": "A streaming service and production company.",
        "keywords": ["AWS", "Microservices", "Distributed Systems", "Java", "Python", "Data Science", "Machine Learning", "Recommendation Systems", "Streaming", "Cloud Native", "DevOps", "Big Data", "User Experience (UX)", "Content Delivery Networks (CDN)", "Video Encoding", "Personalization", "A/B Testing", "Chaos Engineering"]
    },
    "Salesforce": {
        "description": "A cloud-based software company providing customer relationship management (CRM) service.",
        "keywords": ["Salesforce", "CRM", "Apex", "Lightning Web Components", "Cloud Computing", "SaaS", "Enterprise Software", "Customer Success", "Data Analytics", "Integration (MuleSoft)", "Platform Development", "Marketing Cloud", "Service Cloud", "Einstein AI", "Tableau", "Slack"]
    },
    "Generic Tech Startup": {
        "description": "A fast-paced, innovative technology company, often focused on new technologies and agile development.",
        "keywords": ["Agile", "Scrum", "Fast-paced", "Innovation", "MVP", "Growth Hacking", "Fullstack Development", "React", "Node.js", "Python", "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Problem Solving", "Adaptability", "Entrepreneurship", "Cross-functional Teams", "Product-led Growth", "Seed Funding", "Series A/B"]
    },
    "IBM": {
        "description": "An American multinational technology and consulting company, specializing in computer hardware, middleware, and software.",
        "keywords": ["Cloud Computing (IBM Cloud)", "AI (Watson)", "Enterprise Solutions", "Blockchain", "Quantum Computing", "Consulting", "Hybrid Cloud", "Data Analytics", "Java", "Linux", "Mainframe", "Cybersecurity", "Red Hat", "OpenShift", "Automation (RPA)", "IT Services", "Storage Solutions", "Server Technologies"]
    },
    "Oracle": {
        "description": "A multinational computer technology corporation best known for its database software and cloud engineered systems.",
        "keywords": ["Oracle Database", "SQL", "Cloud Infrastructure (OCI)", "ERP (Fusion Applications)", "CRM", "Java", "Enterprise Software", "SaaS", "Data Warehousing", "Middleware", "Cloud Applications", "NetSuite", "Peoplesoft", "Supply Chain Management"]
    },
    "Cisco": {
        "description": "An American multinational digital communications technology conglomerate corporation that develops, manufactures, and sells networking hardware, software, telecommunications equipment, and other high-technology services and products.",
        "keywords": ["Networking", "Cybersecurity (Talos, Duo, Meraki)", "Routers", "Switches", "Collaboration Tools (Webex)", "Cloud Networking", "IoT", "Enterprise Security", "SD-WAN", "Python (for automation)", "Network Automation", "Data Center Networking", "Voice over IP (VoIP)", "Firewalls"]
    },
    "Adobe": {
        "description": "An American multinational computer software company that has historically focused upon the creation of multimedia and creativity software products.",
        "keywords": ["Creative Cloud", "Photoshop", "Illustrator", "Premiere Pro", "Experience Cloud", "Digital Marketing", "SaaS", "Cloud Computing", "User Interface (UI)", "User Experience (UX)", "Web Development", "Content Management", "Analytics (Adobe Analytics)", "Targeting", "Audience Management", "AI (Sensei)", "Video Editing", "Graphic Design"]
    },
    "SAP": {
        "description": "A German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
        "keywords": ["ERP (SAP S/4HANA)", "CRM", "Cloud Computing", "Business Intelligence (SAP BW/4HANA)", "Supply Chain Management", "Procurement", "Financial Software", "ABAP", "Enterprise Solutions", "SaaS", "SAP Fiori", "Data Warehousing", "SAP Concur", "Ariba"]
    },
    "Intel": {
        "description": "An American multinational corporation and technology company that is the world's largest semiconductor chip manufacturer by revenue.",
        "keywords": ["Semiconductors", "Processors (CPUs)", "Microarchitecture", "Hardware Engineering", "Chip Design", "Manufacturing", "IoT", "AI Accelerators", "Cloud Computing Infrastructure", "Embedded Systems", "Security (McAfee)", "FPGA", "Xeon", "Core", "Ecosystem Development"]
    },
    "NVIDIA": {
        "description": "A global technology company that designs graphics processing units (GPUs) for the gaming, professional visualization, data center, and automotive markets.",
        "keywords": ["GPU", "AI", "Deep Learning", "Machine Learning", "CUDA", "Computer Graphics", "High-Performance Computing (HPC)", "Gaming", "Autonomous Vehicles", "Data Center", "TensorFlow", "PyTorch", "Robotics (Isaac)", "Virtual Reality", "Ray Tracing", "Simulation (Omniverse)"]
    },
    "Tesla": {
        "description": "An American multinational automotive and clean energy company.",
        "keywords": ["Electric Vehicles (EV)", "Battery Technology", "AI", "Autonomous Driving", "Robotics", "Software Engineering (Automotive)", "Manufacturing", "Energy Storage", "Machine Learning (Computer Vision)", "Embedded Systems", "Gigafactory", "Powerwall", "Supercharger Network"]
    },
    "SpaceX": {
        "description": "An American spacecraft manufacturer, launch service provider, and satellite communications company.",
        "keywords": ["Aerospace Engineering", "Rocketry", "Satellite Communications (Starlink)", "Propulsion", "Manufacturing", "Software Engineering (Aerospace)", "Embedded Systems", "Guidance, Navigation, and Control (GNC)", "Reusable Rockets", "Space Exploration", "Avionics", "Ground Systems"]
    },
    "Zoom": {
        "description": "A communications technology company providing video telephony and online chat services.",
        "keywords": ["Video Conferencing", "Real-time Communication", "Cloud Infrastructure", "Scalability", "Audio/Video Processing", "Network Protocols", "Security", "SaaS", "Collaboration Tools", "Web Development (WebRTC)", "API Integration", "User Interface (UI)"]
    },
    "ServiceNow": {
        "description": "An American software company that develops a cloud computing platform to help companies manage digital workflows for enterprise operations.",
        "keywords": ["ITSM", "HRSD", "CSM", "Workflow Automation", "Cloud Platform", "Enterprise Software", "SaaS", "Low-code/No-code", "Integration", "Digital Transformation", "Platform Development (Now Platform)", "Service Management", "Operations Management", "Security Operations"]
    },
    "Workday": {
        "description": "An American on-demand (cloud-based) financial management and human capital management software vendor.",
        "keywords": ["HCM (Human Capital Management)", "Financial Management", "SaaS", "Cloud Computing", "Enterprise Software", "Data Analytics", "HRIS", "Payroll", "Talent Management", "Reporting", "Adaptive Planning", "Recruiting", "Benefits Administration"]
    },
    "T-Mobile (US)": {
        "description": "A major American wireless network operator.",
        "keywords": ["Telecommunications", "5G", "Wireless Networks", "Mobile Technology", "Network Engineering", "Customer Experience", "IoT Connectivity", "VoIP", "Fiber Optics", "Cloud Native (Telecom)", "Billing Systems"]
    },
    "Verizon": {
        "description": "An American multinational telecommunications conglomerate and a wireless network operator.",
        "keywords": ["Telecommunications", "5G", "Wireless Networks", "Fiber Optic Networks", "IoT", "Enterprise Solutions", "Network Security", "Cloud Services", "Edge Computing", "Media & Entertainment (Verizon Media)", "Digital Marketing"]
    },
    "AT&T": {
        "description": "An American multinational telecommunications holding company.",
        "keywords": ["Telecommunications", "5G", "Fiber Optics", "Wireless Services", "Broadband", "Network Infrastructure", "Cybersecurity", "Entertainment (Warner Bros. Discovery)", "IoT Solutions", "Enterprise Connectivity"]
    },
    "Qualcomm": {
        "description": "A global semiconductor company that designs and markets wireless telecommunications products and services.",
        "keywords": ["Semiconductors", "Mobile Processors (Snapdragon)", "5G Technology", "Wireless Communication", "IoT", "Automotive (ADAS)", "Chip Design", "Embedded Systems", "AI Processors", "RF Front End", "Modems"]
    },
    "Broadcom": {
        "description": "A global infrastructure technology company designing, developing, and supplying a broad range of semiconductor and infrastructure software solutions.",
        "keywords": ["Semiconductors", "Networking Hardware", "Storage Solutions", "Broadband Communication", "Enterprise Software", "Cybersecurity (Symantec)", "Mainframe Software (CA Technologies)", "Fiber Optics", "Wireless Connectivity"]
    },
    "VMware (now Broadcom subsidiary)": {
        "description": "A cloud computing and virtualization technology company, now part of Broadcom.",
        "keywords": ["Virtualization", "Cloud Computing", "Data Center", "SDDC (Software-Defined Data Center)", "Network Virtualization (NSX)", "Storage Virtualization (vSAN)", "Hybrid Cloud", "Multi-Cloud", "Containerization (Tanzu)", "Kubernetes", "VMs (Virtual Machines)", "VDI (Virtual Desktop Infrastructure)"]
    },
    "Palo Alto Networks": {
        "description": "A global cybersecurity leader providing enterprise security solutions.",
        "keywords": ["Cybersecurity", "Network Security", "Cloud Security", "Endpoint Security", "Firewalls", "Threat Detection", "Incident Response", "AI in Security", "Machine Learning in Security", "Zero Trust", "Security Operations (SecOps)", "SaaS Security"]
    },
    "CrowdStrike": {
        "description": "A cybersecurity technology company focused on endpoint protection.",
        "keywords": ["Cybersecurity", "Endpoint Detection and Response (EDR)", "Cloud Security", "Threat Intelligence", "Incident Response", "AI in Security", "Machine Learning", "XDR (Extended Detection and Response)", "Security Analytics", "Cloud Native Security"]
    },
    "Snowflake": {
        "description": "A cloud-based data warehousing company offering a data cloud platform.",
        "keywords": ["Data Warehousing", "Cloud Data Platform", "SQL", "Big Data", "Data Lakes", "Data Sharing", "Data Governance", "Analytics", "Machine Learning (Data)", "Snowflake Native Apps", "Data Engineering", "Performance Optimization"]
    },
    "Databricks": {
        "description": "A company providing a cloud-based data lakehouse platform for data science and AI.",
        "keywords": ["Data Lakehouse", "Spark", "Data Science", "Machine Learning", "AI", "Big Data", "Data Engineering", "Delta Lake", "MLflow", "Lakehouse Architecture", "Python", "Scala", "SQL", "Data Bricks Runtime"]
    },
    "ServiceNow": {
        "description": "An American software company that develops a cloud computing platform to help companies manage digital workflows for enterprise operations.",
        "keywords": ["ITSM", "HRSD", "CSM", "Workflow Automation", "Cloud Platform", "Enterprise Software", "SaaS", "Low-code/No-code", "Integration", "Digital Transformation", "Platform Development (Now Platform)", "Service Management", "Operations Management", "Security Operations"]
    },
    "Okta": {
        "description": "A leading independent provider of identity for the enterprise.",
        "keywords": ["Identity and Access Management (IAM)", "Single Sign-On (SSO)", "Multi-Factor Authentication (MFA)", "Cloud Security", "API Security", "Enterprise Security", "Zero Trust", "AuthN/AuthZ"]
    },
    "Zscaler": {
        "description": "A cloud security company offering a cloud-native security platform.",
        "keywords": ["Cloud Security", "Zero Trust Network Access (ZTNA)", "SASE (Secure Access Service Edge)", "Network Security", "Cybersecurity", "Secure Web Gateway (SWG)", "Cloud Firewall", "Proxy Services"]
    },
    "Twilio": {
        "description": "A cloud communications platform as a service (CPaaS) company.",
        "keywords": ["CPaaS", "APIs", "Cloud Communications", "SMS", "Voice", "Video", "Email", "Customer Engagement", "Programmable Communications", "Twilio Segment (CDP)", "Twilio Flex (Contact Center)"]
    },
    "Shopify": {
        "description": "A leading e-commerce platform for online stores and retail point-of-sale systems.",
        "keywords": ["E-commerce", "SaaS", "Online Retail", "Shopify Plus", "Payment Gateways", "Logistics", "Inventory Management", "Marketing Automation", "Web Development", "Ruby on Rails", "React", "Store Management"]
    },
    "Square (Block, Inc.)": {
        "description": "A financial services and mobile payment company.",
        "keywords": ["FinTech", "Mobile Payments", "Payment Processing", "Point-of-Sale (POS)", "SME Solutions", "Cash App", "Bitcoin (Square Crypto)", "Business Banking", "Hardware (Readers)", "Blockchain"]
    },
    "Stripe": {
        "description": "A financial technology company offering payment processing software and APIs.",
        "keywords": ["FinTech", "Payment Gateway", "API", "Online Payments", "SaaS", "Billing", "Fraud Prevention", "Global Payments", "Developer Tools", "Financial Infrastructure", "Stripe Connect"]
    },
    "DocuSign": {
        "description": "A company providing electronic signature technology and digital transaction management services.",
        "keywords": ["Electronic Signature", "Digital Transformation", "SaaS", "Workflow Automation", "Document Management", "Legal Tech", "Compliance", "Cloud Security", "API Integration"]
    },
    "Coupa Software": {
        "description": "A business spend management (BSM) software company.",
        "keywords": ["Procurement Software", "Spend Management", "SaaS", "Cloud Computing", "Supply Chain Management", "Financial Software", "Contract Management", "Expense Management"]
    },
    "Workday": {
        "description": "An American on-demand (cloud-based) financial management and human capital management software vendor.",
        "keywords": ["HCM", "Financial Management", "SaaS", "Cloud Computing", "Enterprise Software", "Data Analytics", "HRIS", "Payroll", "Talent Management", "Reporting"]
    },
    "Zendesk": {
        "description": "A customer service software company building products designed to improve customer relationships.",
        "keywords": ["Customer Service", "CRM", "SaaS", "Help Desk Software", "Ticketing System", "Customer Support", "Chatbot", "Knowledge Base", "Customer Experience (CX)", "Analytics"]
    },
    "Splunk": {
        "description": "A software company that produces software for searching, monitoring, and analyzing machine-generated big data.",
        "keywords": ["Big Data", "Data Analytics", "Machine Data", "SIEM (Security Information and Event Management)", "IT Operations", "Cybersecurity", "Observability", "Monitoring", "Log Management", "Search Technology", "Dashboards"]
    },
    "Datadog": {
        "description": "A monitoring and analytics platform for developers, IT operations teams and business users.",
        "keywords": ["Monitoring", "Observability", "Cloud Monitoring", "Application Performance Monitoring (APM)", "Log Management", "Infrastructure Monitoring", "Security Monitoring", "DevOps", "Kubernetes Monitoring", "Cloud Native"]
    },
    "PwC": {
        "description": "A multinational professional services network, providing audit, assurance, consulting, and tax services.",
        "keywords": ["Consulting", "Digital Transformation", "Cybersecurity Consulting", "Cloud Strategy", "Data Analytics Consulting", "Enterprise Architecture", "Technology Advisory", "ERP Implementation", "Financial Consulting", "Management Consulting"]
    },
    "Deloitte": {
        "description": "One of the 'Big Four' accounting organizations and the largest professional services network by revenue and number of professionals.",
        "keywords": ["Consulting", "IT Consulting", "Digital Transformation", "Cybersecurity Consulting", "Cloud Strategy", "Data Science Consulting", "AI Strategy", "Enterprise Solutions", "Risk Advisory", "Strategy Consulting"]
    },
    "EY (Ernst & Young)": {
        "description": "A multinational professional services firm, one of the 'Big Four' accounting firms.",
        "keywords": ["Consulting", "Technology Consulting", "Digital Transformation", "Cybersecurity", "Data Analytics", "Cloud Services", "AI & Automation", "Strategy & Transactions", "Advisory Services"]
    },
    "KPMG": {
        "description": "A multinational professional services network, and one of the 'Big Four' accounting organizations.",
        "keywords": ["Consulting", "Digital Transformation", "Cybersecurity", "Cloud Advisory", "Data & Analytics", "Emerging Technologies", "Risk Consulting", "Financial Services Consulting", "Technology Implementation"]
    },
    # Indian Companies - IT Services & Consulting
    "Tata Consultancy Services (TCS)": {
        "description": "A leading global IT services, consulting, and business solutions organization and part of the Tata Group.",
        "keywords": ["IT Services", "Consulting", "Digital Transformation", "Cloud Computing", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Cybersecurity", "IoT", "Agile", "DevOps", "Java", "Python", "SAP", "Oracle", "Automation", "Blockchain", "Financial Services", "Manufacturing", "Cognitive Business Operations", "Assurance Services", "Engineering & Industrial Services"]
    },
    "Infosys": {
        "description": "A global leader in next-generation digital services and consulting.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "IoT", "Automation", "Enterprise Applications", "SAP", "Oracle", "Java", "Python", "Big Data", "DevOps", "Blockchain", "Consulting", "Digital Experience", "Legacy Modernization", "Finacle (Banking Software)"]
    },
    "Wipro": {
        "description": "A global information technology, consulting, and business process services company.",
        "keywords": ["IT Services", "Consulting", "Digital Transformation", "Cloud Computing", "AI", "Machine Learning", "Data Science", "Cybersecurity", "IoT", "Automation", "DevOps", "SAP", "Oracle", "Java", "Python", "Analytics", "Blockchain", "Industry Solutions", "Application Development & Management", "Infrastructure Services"]
    },
    "HCLTech": {
        "description": "A global technology company that helps enterprises reimagine their businesses for the digital age.",
        "keywords": ["Digital Engineering", "Cloud Adoption", "IoT Solutions", "Automation", "Security", "Analytics", "Digital Transformation", "AI", "Machine Learning", "Cybersecurity", "Fullstack Development", "Cloud Native", "DevOps", "Enterprise Applications", "Product Engineering", "Infrastructure Modernization"]
    },
    "Tech Mahindra": {
        "description": "An Indian multinational information technology services and consulting company.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Cybersecurity", "Network Services", "Business Process Services", "Enterprise Applications", "Engineering Services", "Blockchain", "5G", "IoT", "Robotics", "Telecommunications", "CRM Services", "Data Analytics"]
    },
    "LTIMindtree": {
        "description": "An Indian multinational information technology services and consulting company, formed by the merger of L&T Infotech and Mindtree.",
        "keywords": ["IT Services", "Digital Transformation", "Cloud Computing", "Data & Analytics", "Generative AI", "Application Development", "Cybersecurity", "Enterprise Solutions", "IoT", "DevOps", "Agile", "Consulting", "Product Engineering", "Customer Experience (CX)", "SAP", "Oracle"]
    },
    "Cognizant": {
        "description": "A global information technology services and consulting company with a significant presence in India.",
        "keywords": ["IT Consulting", "Digital Strategy", "Cloud Solutions", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "Application Development", "Business Process Services", "Industry Solutions", "DevOps", "Agile", "Digital Engineering", "Enterprise Transformation"]
    },
    "Capgemini (India Operations)": {
        "description": "A global leader in consulting, technology services, and digital transformation, with strong operations in India.",
        "keywords": ["Consulting", "IT Services", "Digital Transformation", "Cloud Computing", "AI", "Data Analytics", "Cybersecurity", "Application Services", "DevOps", "Agile", "SAP", "Oracle", "Industry Expertise", "Intelligent Automation", "Customer Experience"]
    },
    "Persistent Systems": {
        "description": "A global services company that provides software product development and technology services.",
        "keywords": ["Product Engineering", "Digital Engineering", "Cloud Native", "Data & AI", "Enterprise Modernization", "Software Development", "Agile", "DevOps", "Banking & Financial Services (BFS)", "Healthcare Tech", "Life Sciences", "IoT Solutions"]
    },
    "Mphasis": {
        "description": "A global information technology solutions provider specializing in cloud and cognitive services.",
        "keywords": ["Cloud Transformation", "AI", "Cognitive Technologies", "Digital Transformation", "DevOps", "Automation", "Cybersecurity", "Data Analytics", "IT Services", "Blockchain", "Application Modernization", "Financial Services Tech"]
    },
    "Coforge (formerly NIIT Technologies)": {
        "description": "A global IT solutions organization enabling businesses to transform with digital technologies.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Automation", "Cybersecurity", "Application Development", "Microservices", "API Management", "Travel Tech", "Financial Services"]
    },
    # Indian Companies - Startups & Product Companies
    "Reliance Jio Platforms": {
        "description": "A technology company providing digital services, including mobile connectivity, broadband, and various digital platforms.",
        "keywords": ["5G", "Telecommunications", "Digital Services", "Cloud Platforms", "AI", "IoT", "Big Data", "Mobile Technology", "Fixed Wireless Access (FWA)", "E-commerce (JioMart)", "FinTech (JioMoney)", "Content Streaming (JioCinema)", "Fiber Optics", "Digital Payments", "Edge Computing"]
    },
    "Flipkart": {
        "description": "An Indian e-commerce company, a subsidiary of Walmart, offering a wide range of products.",
        "keywords": ["E-commerce", "Supply Chain", "Logistics", "Retail Technology", "Mobile Development", "Android", "iOS", "Data Science", "Machine Learning (Recommendations)", "Cloud Infrastructure (AWS, GCP)", "Microservices", "Payments", "Fraud Detection", "Personalization", "Big Data", "Customer Experience"]
    },
    "Zomato": {
        "description": "An Indian multinational restaurant aggregator and food delivery company.",
        "keywords": ["Food Delivery", "Restaurant Technology", "Logistics", "Mobile Development", "Data Analytics", "Machine Learning (Recommendation Systems)", "Cloud Infrastructure (AWS)", "Geolocation", "Payment Gateways", "User Experience (UX)", "Growth Hacking", "Hyperlocal", "Mapping", "Real-time Systems"]
    },
    "Swiggy": {
        "description": "An Indian online food ordering and delivery platform.",
        "keywords": ["Food Delivery", "Quick Commerce (Instamart)", "Logistics Optimization", "Mobile Development", "Data Science", "Machine Learning", "Real-time Systems", "Cloud Platforms (AWS)", "Geolocation", "Payments", "User Experience (UX)", "Route Optimization", "Demand Forecasting"]
    },
    "Paytm": {
        "description": "An Indian multinational financial technology company specializing in digital payment systems, e-commerce, and financial services.",
        "keywords": ["FinTech", "Digital Payments", "Mobile Wallets", "UPI", "E-commerce", "Financial Services", "Blockchain", "Cybersecurity", "Data Analytics", "Fraud Detection", "Cloud Computing", "Microservices", "Scalability", "Security", "Investment Tech", "Lending", "Insurance Tech"]
    },
    "Ola": {
        "description": "An Indian multinational ridesharing company offering transportation, food delivery, and financial services.",
        "keywords": ["Ridesharing", "Mobility Solutions", "Electric Vehicles (EV)", "Logistics", "Geolocation", "Mobile Development", "Data Science", "Machine Learning (Pricing, Routing)", "Cloud Platforms (AWS)", "Payment Systems", "User Experience", "Fleet Management", "Mapping", "Autonomous Driving (early stages)"]
    },
    "BYJU'S": {
        "description": "An Indian multinational educational technology company, providing online tutoring and learning programs.",
        "keywords": ["EdTech", "Online Learning", "Content Creation (Video, Animation)", "Mobile App Development", "AI (Personalized Learning)", "Machine Learning", "Data Analytics (Student Progress)", "Curriculum Development", "User Experience", "Subscription Models", "Gamification", "Adaptive Learning", "K-12 Education"]
    },
    "CRED": {
        "description": "A members-only credit card bill payment platform that rewards its members for clearing their credit card bills on time.",
        "keywords": ["FinTech", "Credit Scoring", "Payments", "Data Analytics", "User Experience (UX)", "Mobile App Development", "Security", "Wealth Management (early stages)", "Loyalty Programs", "Personal Finance"]
    },
    "Razorpay": {
        "description": "A leading Indian fintech company that provides payment solutions for businesses of all sizes.",
        "keywords": ["FinTech", "Payment Gateway", "API", "Online Payments", "UPI", "Payment Processing", "SME Solutions", "Banking Tech", "Neo-banking", "Payroll Management", "Fraud Detection", "Data Analytics", "Scalability"]
    },
    "PhonePe": {
        "description": "An Indian digital payments and financial services company, a subsidiary of Flipkart.",
        "keywords": ["FinTech", "Digital Payments", "UPI", "Mobile Wallets", "Financial Services", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Geolocation", "Security", "Data Analytics", "Scalability"]
    },
    "Meesho": {
        "description": "An Indian social commerce platform enabling small businesses and individuals to start online businesses without investment.",
        "keywords": ["E-commerce", "Social Commerce", "Reselling", "Logistics", "Supply Chain", "Mobile Development", "Data Science", "Machine Learning (Recommendations)", "Payments", "User Acquisition", "Growth Hacking", "Tier 2/3 Markets"]
    },
    "Dream11": {
        "description": "An Indian fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "BYJU'S": {
        "description": "An Indian multinational educational technology company, providing online tutoring and learning programs.",
        "keywords": ["EdTech", "Online Learning", "Content Creation", "Mobile App Development", "AI (Personalized Learning)", "Machine Learning", "Data Analytics", "Curriculum Development", "User Experience", "Subscription Models"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "PolicyBazaar": {
        "description": "An Indian online insurance aggregator and financial services company.",
        "keywords": ["FinTech", "Insurance Tech (InsurTech)", "Online Aggregator", "Digital Marketing", "Lead Generation", "Data Analytics", "AI (Recommendations)", "Customer Service Tech", "Web Development", "Mobile App Development"]
    },
    "Nykaa": {
        "description": "An Indian e-commerce company for beauty, wellness, and fashion products.",
        "keywords": ["E-commerce", "Retail Tech", "Beauty & Fashion Tech", "Online Shopping", "Logistics", "Inventory Management", "Digital Marketing", "Personalization", "Mobile App Development", "Customer Experience (CX)"]
    },
    "Udaan": {
        "description": "An Indian B2B e-commerce platform for small and medium businesses.",
        "keywords": ["B2B E-commerce", "Supply Chain", "Logistics", "FinTech (Lending)", "Wholesale Trade", "Marketplace", "Data Analytics", "Mobile Platform", "Small Business Solutions", "Procurement"]
    },
    "BrowserStack": {
        "description": "A cloud web and mobile testing platform.",
        "keywords": ["Testing Automation", "Cloud Testing", "Browser Compatibility", "Mobile Testing", "SaaS", "DevOps Tools", "Continuous Integration/Continuous Delivery (CI/CD)", "Quality Assurance (QA)", "Selenium", "Appium"]
    },
    "Freshworks": {
        "description": "A global software company providing SaaS customer engagement solutions.",
        "keywords": ["SaaS", "CRM", "Help Desk Software", "Customer Service", "ITSM", "Sales Automation", "Marketing Automation", "AI Chatbots", "Customer Engagement", "Cloud Computing"]
    },
    "Druva": {
        "description": "A cloud data protection and management company.",
        "keywords": ["Cloud Data Protection", "Data Backup", "Disaster Recovery", "Data Governance", "Cybersecurity", "SaaS", "Cloud Computing", "Data Resilience", "Compliance", "Security Automation"]
    },
    "Postman": {
        "description": "A leading API development and testing platform.",
        "keywords": ["API Development", "API Testing", "Developer Tools", "Collaboration Tools", "API Management", "RESTful APIs", "GraphQL", "Microservices", "DevOps", "Software Development Lifecycle (SDLC)"]
    },
    "Amagi": {
        "description": "A global leader in cloud-based SaaS technology for broadcast and streaming TV.",
        "keywords": ["Cloud TV", "Broadcast Technology", "Streaming Media", "SaaS", "Video On Demand (VOD)", "Live Streaming", "Content Delivery Networks (CDN)", "Ad Insertion", "Media Technology", "AWS", "GCP"]
    },
    "Chargebee": {
        "description": "A subscription billing and revenue management platform for SaaS and subscription businesses.",
        "keywords": ["SaaS", "Subscription Management", "Billing Software", "Revenue Operations", "Payment Gateways", "FinTech", "Recurring Revenue", "Stripe", "Zuora", "Financial Analytics"]
    },
    "CleverTap": {
        "description": "A leading customer engagement and retention platform for mobile apps.",
        "keywords": ["Mobile Marketing", "Customer Engagement", "Retention Marketing", "Personalization", "Data Analytics", "AI (Marketing)", "Machine Learning", "Push Notifications", "In-App Messaging", "Customer Data Platform (CDP)"]
    },
    "Unacademy": {
        "description": "An Indian online education technology company.",
        "keywords": ["EdTech", "Online Learning", "Live Classes", "Test Preparation", "Content Creation", "Mobile App Development", "Data Analytics (Learning)", "Personalized Learning"]
    },
    "Vedantu": {
        "description": "An Indian online tutoring platform providing live interactive classes.",
        "keywords": ["EdTech", "Online Tutoring", "Live Classes", "Personalized Learning", "Mobile App Development", "Learning Management Systems (LMS)", "AI (Learning Analytics)", "Gamification"]
    },
    "Urban Company": {
        "description": "An Indian at-home services platform.",
        "keywords": ["On-demand Services", "Hyperlocal", "Mobile App Development", "Logistics", "Geolocation", "Service Marketplace", "User Experience (UX)", "Payment Systems"]
    },
    "MakeMyTrip": {
        "description": "An Indian online travel company providing travel services and products.",
        "keywords": ["Travel Tech", "Online Travel Agency (OTA)", "Flight Booking", "Hotel Booking", "Holiday Packages", "Mobile App Development", "E-commerce", "Payment Gateways", "Recommendation Systems"]
    },
    "Bykea": { # Pakistani but similar market dynamics
        "description": "A Pakistani on-demand ride-hailing, logistics, and payments company.",
        "keywords": ["Ridesharing", "Logistics", "FinTech (Payments)", "On-demand Services", "Hyperlocal", "Mobile App Development", "Geolocation", "Last-Mile Delivery"]
    },
    # Global Companies - Other sectors
    "Salesforce": {
        "description": "A cloud-based software company providing customer relationship management (CRM) service.",
        "keywords": ["Salesforce", "CRM", "Apex", "Lightning Web Components", "Cloud Computing", "SaaS", "Enterprise Software", "Customer Success", "Data Analytics", "Integration", "Platform Development"]
    },
    "Intuit": {
        "description": "A global technology platform that helps consumers and small businesses prosper with financial management solutions.",
        "keywords": ["FinTech", "Accounting Software (QuickBooks)", "Tax Software (TurboTax)", "Personal Finance (Mint)", "Small Business Solutions", "SaaS", "Data Analytics", "AI in Finance", "Cloud Accounting", "Payroll", "Payment Processing"]
    },
    "SAP": {
        "description": "A German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
        "keywords": ["ERP", "CRM", "S/4HANA", "Cloud Computing", "Business Intelligence", "Supply Chain Management", "Procurement", "Financial Software", "ABAP", "Enterprise Solutions", "SaaS"]
    },
    "Siemens AG": {
        "description": "A global technology powerhouse focusing on industry, infrastructure, transport, and healthcare.",
        "keywords": ["Industrial IoT", "Automation", "Digital Twin", "Smart Infrastructure", "Mobility Solutions", "Healthcare Technology", "Software Engineering (Industrial)", "AI in Manufacturing", "Edge Computing", "Cybersecurity (Industrial)"]
    },
    "GE Digital": {
        "description": "A subsidiary of General Electric, focusing on industrial IoT software and services.",
        "keywords": ["Industrial IoT", "Asset Performance Management (APM)", "Digital Twin", "Data Analytics (Industrial)", "Cloud Platforms", "Cybersecurity (OT/IT)", "Predictive Maintenance", "Operational Technology (OT)"]
    },
    "ABB": {
        "description": "A leading global technology company that energizes the transformation of society and industry to achieve a more productive, sustainable future.",
        "keywords": ["Industrial Automation", "Robotics", "Power Grids", "Electrification", "Motion Control", "IoT", "Digital Transformation (Industry)", "Control Systems", "Sustainable Technologies"]
    },
    "Honeywell": {
        "description": "A diversified technology and manufacturing company with segments in aerospace, building technologies, performance materials, and safety and productivity solutions.",
        "keywords": ["Industrial IoT", "Automation", "Aerospace Systems", "Building Management Systems", "Supply Chain Software", "Cybersecurity (Industrial)", "Control Systems", "Sensing Technologies", "Connected Solutions"]
    },
    "Schneider Electric": {
        "description": "A global specialist in energy management and automation.",
        "keywords": ["Energy Management", "Industrial Automation", "IoT", "Smart Buildings", "Data Center Solutions", "Renewable Energy", "Digital Transformation (Energy)", "Edge Computing", "Power Management", "Sustainability Tech"]
    },
    "Qualtrics": {
        "description": "An experience management company, helping organizations manage customer, employee, product, and brand experiences.",
        "keywords": ["Experience Management (XM)", "Customer Experience (CX)", "Employee Experience (EX)", "Survey Software", "Data Analytics", "Sentiment Analysis", "AI in CX", "Feedback Management", "SaaS"]
    },
    "ServiceNow": {
        "description": "An American software company that develops a cloud computing platform to help companies manage digital workflows for enterprise operations.",
        "keywords": ["ITSM", "HRSD", "CSM", "Workflow Automation", "Cloud Platform", "Enterprise Software", "SaaS", "Low-code/No-code", "Integration", "Digital Transformation", "Platform Development"]
    },
    "Workday": {
        "description": "An American on-demand (cloud-based) financial management and human capital management software vendor.",
        "keywords": ["HCM", "Financial Management", "SaaS", "Cloud Computing", "Enterprise Software", "Data Analytics", "HRIS", "Payroll", "Talent Management", "Reporting"]
    },
    "ZoomInfo": {
        "description": "A leading go-to-market intelligence platform for sales and marketing teams.",
        "keywords": ["Go-to-Market (GTM)", "Sales Intelligence", "Marketing Intelligence", "Lead Generation", "Data Analytics", "CRM Integration", "SaaS", "B2B Data", "Predictive Analytics"]
    },
    "Asana": {
        "description": "A web and mobile application designed to help teams organize, track, and manage their work.",
        "keywords": ["Project Management", "Work Management", "Collaboration Tools", "SaaS", "Agile Project Management", "Workflow Automation", "Task Management", "Team Productivity"]
    },
    "Atlassian": {
        "description": "A software company that develops products for software developers, project managers, and other software development teams.",
        "keywords": ["Jira", "Confluence", "Trello", "Bitbucket", "DevOps Tools", "Project Management", "Team Collaboration", "Agile Software Development", "SaaS", "Cloud Tools", "Enterprise Software"]
    },
    "HubSpot": {
        "description": "A developer and marketer of software products for inbound marketing, sales, and customer service.",
        "keywords": ["CRM", "Marketing Automation", "Sales Software", "Customer Service Software", "SaaS", "Inbound Marketing", "Content Management System (CMS)", "Website Builder", "Email Marketing", "Analytics"]
    },
    "Stripe": {
        "description": "A financial technology company offering payment processing software and APIs.",
        "keywords": ["FinTech", "Payment Gateway", "API", "Online Payments", "SaaS", "Billing", "Fraud Prevention", "Global Payments", "Developer Tools", "Financial Infrastructure"]
    },
    "Adyen": {
        "description": "A global payment company providing payment solutions for businesses.",
        "keywords": ["FinTech", "Payment Processing", "Online Payments", "Point-of-Sale (POS)", "Global Payments", "Fraud Prevention", "Payment Gateway", "API", "Merchant Services"]
    },
    "Fiserv": {
        "description": "A global provider of financial services technology solutions.",
        "keywords": ["FinTech", "Payment Processing", "Core Banking", "Digital Banking", "Financial Technology", "Enterprise Software", "Risk Management (Financial)", "Data Analytics (Financial)"]
    },
    "Fidelity National Information Services (FIS)": {
        "description": "A global leader in financial services technology, specializing in payment processing and banking solutions.",
        "keywords": ["FinTech", "Payment Processing", "Banking Technology", "Capital Markets Solutions", "Enterprise Payments", "Fraud & Risk Management", "Wealth Management Tech", "Blockchain (Financial)"]
    },
    "Illumina": {
        "description": "A company that develops, manufactures, and markets integrated systems for large-scale analysis of genetic variation and function.",
        "keywords": ["Bioinformatics", "Genomics", "Life Sciences", "Data Analysis (Genomics)", "Sequencing Technology", "Biotech", "Research & Development", "Machine Learning (Genetics)"]
    },
    "Moderna": {
        "description": "A biotechnology company focused on drug discovery, drug development, and vaccine technologies based on messenger RNA (mRNA).",
        "keywords": ["Biotechnology", "mRNA Technology", "Drug Discovery", "Vaccine Development", "Genomics", "Bioinformatics", "Clinical Trials", "Research & Development", "Life Sciences"]
    },
    "Guardant Health": {
        "description": "A precision oncology company focused on developing and commercializing proprietary blood tests for cancer.",
        "keywords": ["Biotech", "Healthcare Tech", "Precision Oncology", "Liquid Biopsy", "Genomics", "Data Analytics (Healthcare)", "Machine Learning (Diagnostics)", "Medical Devices", "Molecular Diagnostics"]
    },
    "Intuitive Surgical": {
        "description": "A company that develops, manufactures, and markets robotic products designed to improve clinical outcomes of patients through minimally invasive surgery.",
        "keywords": ["Robotics (Surgical)", "Medical Devices", "Healthcare Tech", "Minimally Invasive Surgery", "Computer Vision (Medical)", "Haptics", "AI in Healthcare", "Embedded Systems", "Hardware Engineering (Medical)"]
    },
    "GE Healthcare": {
        "description": "A leading global medical technology, pharmaceutical diagnostics, and digital solutions innovator.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "AI in Healthcare", "Data Analytics (Healthcare)", "Digital Health", "Precision Health", "Healthcare IT", "Patient Monitoring", "Diagnostic Equipment"]
    },
    "Siemens Healthineers": {
        "description": "A leading medical technology company and independent listed company of Siemens AG, offering products and services for diagnostic and therapeutic purposes.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "Laboratory Diagnostics", "AI in Healthcare", "Digital Health", "Precision Medicine", "Healthcare IT Solutions", "Therapeutic Devices", "Cybersecurity (Healthcare)"]
    },
    "Philips Healthcare": {
        "description": "A diversified technology company focused on improving people's health and well-being through meaningful innovation.",
        "keywords": ["Healthcare Technology", "Medical Devices", "Diagnostic Imaging", "Patient Monitoring", "Connected Care", "Personal Health", "AI in Healthcare", "Digital Health", "Software as a Medical Device (SaMD)"]
    },
    "TSMC (Taiwan Semiconductor Manufacturing Company)": {
        "description": "The world's largest dedicated independent (pure-play) semiconductor foundry.",
        "keywords": ["Semiconductors", "Chip Manufacturing", "Foundry Services", "Process Technology", "Microelectronics", "Wafer Fabrication", "Advanced Packaging", "R&D (Semiconductor)", "Supply Chain (Semiconductor)"]
    },
    "ASML Holding": {
        "description": "A Dutch multinational corporation specializing in the development and manufacturing of photolithography systems for the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Photolithography", "EUV Lithography", "Advanced Manufacturing", "Optics", "Precision Engineering", "Vacuum Technology", "Cleanroom Technology", "High-Tech Manufacturing"]
    },
    "Micron Technology": {
        "description": "An American producer of computer memory and computer data storage including DRAM, NAND flash, and NOR flash.",
        "keywords": ["Semiconductors", "Memory (DRAM, NAND)", "Flash Storage", "Solid State Drives (SSDs)", "Memory Controllers", "Chip Design", "Manufacturing (Memory)", "Data Storage Solutions"]
    },
    "Applied Materials": {
        "description": "A global leader in materials engineering solutions for the semiconductor, flat panel display, and solar photovoltaic industries.",
        "keywords": ["Semiconductor Equipment", "Materials Science", "Process Engineering", "Thin Film Deposition", "Etch Technology", "Ion Implantation", "Metrology", "Yield Management", "Manufacturing (Semiconductor)"]
    },
    "Lam Research": {
        "description": "A global supplier of wafer fabrication equipment and services to the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Wafer Fabrication", "Etch", "Deposition", "Process Control", "Materials Engineering", "Advanced Manufacturing", "R&D (Semiconductor)"]
    },
    "Amdocs": {
        "description": "A multinational corporation that specializes in software and services for communications, media, and financial services providers.",
        "keywords": ["Telecommunications Software", "BSS/OSS", "Digital Transformation (Telecom)", "CRM (Telecom)", "Billing Systems", "Customer Experience (Telecom)", "Cloud Native (Telecom)", "5G Solutions", "Network Management"]
    },
    "Ericsson": {
        "description": "A Swedish multinational networking and telecommunications company.",
        "keywords": ["Telecommunications", "5G Networks", "Mobile Networks", "Radio Access Networks (RAN)", "Network Infrastructure", "IoT Connectivity", "Managed Services", "Network Orchestration", "Cloud Native (Telecom)"]
    },
    "Nokia": {
        "description": "A Finnish multinational telecommunications, information technology, and consumer electronics company.",
        "keywords": ["Telecommunications", "5G Networks", "Network Infrastructure", "Fixed Networks", "Cloud & Network Services", "Optical Networks", "Cybersecurity (Telecom)", "IoT", "Private Wireless Networks"]
    },
    "ZTE Corporation": {
        "description": "A Chinese multinational telecommunications equipment and systems company.",
        "keywords": ["Telecommunications Equipment", "5G Networks", "Wireless Communication", "Optical Communication", "Core Network", "IoT Solutions", "Smart City Solutions", "Network Infrastructure"]
    },
    "SoftBank Group": {
        "description": "A Japanese multinational conglomerate holding company primarily focused on investment in technology, energy, and financial companies.",
        "keywords": ["Investment (Tech)", "Venture Capital", "Vision Fund", "AI Investment", "Telecommunications (SoftBank Corp.)", "ARM Holdings", "Robotics (Boston Dynamics)", "Disruptive Technologies"]
    },
    "Tencent": {
        "description": "A Chinese multinational technology and entertainment conglomerate holding company.",
        "keywords": ["Gaming (Tencent Games)", "Social Media (WeChat)", "FinTech (WeChat Pay)", "Cloud Computing (Tencent Cloud)", "AI", "Content Platforms", "Digital Entertainment", "E-commerce", "Online Advertising"]
    },
    "Alibaba Group": {
        "description": "A Chinese multinational technology company specializing in e-commerce, retail, Internet, and technology.",
        "keywords": ["E-commerce (Taobao, Tmall)", "FinTech (Ant Group, Alipay)", "Cloud Computing (Alibaba Cloud)", "Logistics (Cainiao)", "Digital Media & Entertainment", "AI", "Big Data", "Supply Chain", "Retail Tech"]
    },
    "ByteDance": {
        "description": "A Chinese internet technology company, best known for its video-sharing platform TikTok.",
        "keywords": ["Social Media", "Short-form Video (TikTok)", "Content Recommendation", "AI (Recommendation Algorithms)", "Machine Learning", "Natural Language Processing (NLP)", "Computer Vision", "Content Creation Tools", "AdTech", "Global Scale"]
    },
    "Baidu": {
        "description": "A Chinese multinational technology company specializing in internet-related services and products, and artificial intelligence.",
        "keywords": ["Search Engine", "AI", "Autonomous Driving (Apollo)", "Cloud Computing (Baidu AI Cloud)", "Natural Language Processing (NLP)", "Computer Vision", "Smart Devices", "Digital Assistant (DuerOS)", "Machine Learning", "Big Data"]
    },
    "SAP": {
        "description": "A German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
        "keywords": ["ERP", "CRM", "S/4HANA", "Cloud Computing", "Business Intelligence", "Supply Chain Management", "Procurement", "Financial Software", "ABAP", "Enterprise Solutions", "SaaS"]
    },
    "Siemens AG": {
        "description": "A global technology powerhouse focusing on industry, infrastructure, transport, and healthcare.",
        "keywords": ["Industrial IoT", "Automation", "Digital Twin", "Smart Infrastructure", "Mobility Solutions", "Healthcare Technology", "Software Engineering (Industrial)", "AI in Manufacturing", "Edge Computing", "Cybersecurity (Industrial)"]
    },
    "GE Digital": {
        "description": "A subsidiary of General Electric, focusing on industrial IoT software and services.",
        "keywords": ["Industrial IoT", "Asset Performance Management (APM)", "Digital Twin", "Data Analytics (Industrial)", "Cloud Platforms", "Cybersecurity (OT/IT)", "Predictive Maintenance", "Operational Technology (OT)"]
    },
    "ABB": {
        "description": "A leading global technology company that energizes the transformation of society and industry to achieve a more productive, sustainable future.",
        "keywords": ["Industrial Automation", "Robotics", "Power Grids", "Electrification", "Motion Control", "IoT", "Digital Transformation (Industry)", "Control Systems", "Sustainable Technologies"]
    },
    "Honeywell": {
        "description": "A diversified technology and manufacturing company with segments in aerospace, building technologies, performance materials, and safety and productivity solutions.",
        "keywords": ["Industrial IoT", "Automation", "Aerospace Systems", "Building Management Systems", "Supply Chain Software", "Cybersecurity (Industrial)", "Control Systems", "Sensing Technologies", "Connected Solutions"]
    },
    "Schneider Electric": {
        "description": "A global specialist in energy management and automation.",
        "keywords": ["Energy Management", "Industrial Automation", "IoT", "Smart Buildings", "Data Center Solutions", "Renewable Energy", "Digital Transformation (Energy)", "Edge Computing", "Power Management", "Sustainability Tech"]
    },
    "Qualtrics": {
        "description": "An experience management company, helping organizations manage customer, employee, product, and brand experiences.",
        "keywords": ["Experience Management (XM)", "Customer Experience (CX)", "Employee Experience (EX)", "Survey Software", "Data Analytics", "Sentiment Analysis", "AI in CX", "Feedback Management", "SaaS"]
    },
    "ZoomInfo": {
        "description": "A leading go-to-market intelligence platform for sales and marketing teams.",
        "keywords": ["Go-to-Market (GTM)", "Sales Intelligence", "Marketing Intelligence", "Lead Generation", "Data Analytics", "CRM Integration", "SaaS", "B2B Data", "Predictive Analytics"]
    },
    "Asana": {
        "description": "A web and mobile application designed to help teams organize, track, and manage their work.",
        "keywords": ["Project Management", "Work Management", "Collaboration Tools", "SaaS", "Agile Project Management", "Workflow Automation", "Task Management", "Team Productivity"]
    },
    "Atlassian": {
        "description": "A software company that develops products for software developers, project managers, and other software development teams.",
        "keywords": ["Jira", "Confluence", "Trello", "Bitbucket", "DevOps Tools", "Project Management", "Team Collaboration", "Agile Software Development", "SaaS", "Cloud Tools", "Enterprise Software"]
    },
    "HubSpot": {
        "description": "A developer and marketer of software products for inbound marketing, sales, and customer service.",
        "keywords": ["CRM", "Marketing Automation", "Sales Software", "Customer Service Software", "SaaS", "Inbound Marketing", "Content Management System (CMS)", "Website Builder", "Email Marketing", "Analytics"]
    },
    "Adyen": {
        "description": "A global payment company providing payment solutions for businesses.",
        "keywords": ["FinTech", "Payment Processing", "Online Payments", "Point-of-Sale (POS)", "Global Payments", "Fraud Prevention", "Payment Gateway", "API", "Merchant Services"]
    },
    "Fiserv": {
        "description": "A global provider of financial services technology solutions.",
        "keywords": ["FinTech", "Payment Processing", "Core Banking", "Digital Banking", "Financial Technology", "Enterprise Software", "Risk Management (Financial)", "Data Analytics (Financial)"]
    },
    "Fidelity National Information Services (FIS)": {
        "description": "A global leader in financial services technology, specializing in payment processing and banking solutions.",
        "keywords": ["FinTech", "Payment Processing", "Banking Technology", "Capital Markets Solutions", "Enterprise Payments", "Fraud & Risk Management", "Wealth Management Tech", "Blockchain (Financial)"]
    },
    "Illumina": {
        "description": "A company that develops, manufactures, and markets integrated systems for large-scale analysis of genetic variation and function.",
        "keywords": ["Bioinformatics", "Genomics", "Life Sciences", "Data Analysis (Genomics)", "Sequencing Technology", "Biotech", "Research & Development", "Machine Learning (Genetics)"]
    },
    "Moderna": {
        "description": "A biotechnology company focused on drug discovery, drug development, and vaccine technologies based on messenger RNA (mRNA).",
        "keywords": ["Biotechnology", "mRNA Technology", "Drug Discovery", "Vaccine Development", "Genomics", "Bioinformatics", "Clinical Trials", "Research & Development", "Life Sciences"]
    },
    "Guardant Health": {
        "description": "A precision oncology company focused on developing and commercializing proprietary blood tests for cancer.",
        "keywords": ["Biotech", "Healthcare Tech", "Precision Oncology", "Liquid Biopsy", "Genomics", "Data Analytics (Healthcare)", "Machine Learning (Diagnostics)", "Medical Devices", "Molecular Diagnostics"]
    },
    "Intuitive Surgical": {
        "description": "A company that develops, manufactures, and markets robotic products designed to improve clinical outcomes of patients through minimally invasive surgery.",
        "keywords": ["Robotics (Surgical)", "Medical Devices", "Healthcare Tech", "Minimally Invasive Surgery", "Computer Vision (Medical)", "Haptics", "AI in Healthcare", "Embedded Systems", "Hardware Engineering (Medical)"]
    },
    "GE Healthcare": {
        "description": "A leading global medical technology, pharmaceutical diagnostics, and digital solutions innovator.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "AI in Healthcare", "Data Analytics (Healthcare)", "Digital Health", "Precision Health", "Healthcare IT", "Patient Monitoring", "Diagnostic Equipment"]
    },
    "Siemens Healthineers": {
        "description": "A leading medical technology company and independent listed company of Siemens AG, offering products and services for diagnostic and therapeutic purposes.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "Laboratory Diagnostics", "AI in Healthcare", "Digital Health", "Precision Medicine", "Healthcare IT Solutions", "Therapeutic Devices", "Cybersecurity (Healthcare)"]
    },
    "Philips Healthcare": {
        "description": "A diversified technology company focused on improving people's health and well-being through meaningful innovation.",
        "keywords": ["Healthcare Technology", "Medical Devices", "Diagnostic Imaging", "Patient Monitoring", "Connected Care", "Personal Health", "AI in Healthcare", "Digital Health", "Software as a Medical Device (SaMD)"]
    },
    "TSMC (Taiwan Semiconductor Manufacturing Company)": {
        "description": "The world's largest dedicated independent (pure-play) semiconductor foundry.",
        "keywords": ["Semiconductors", "Chip Manufacturing", "Foundry Services", "Process Technology", "Microelectronics", "Wafer Fabrication", "Advanced Packaging", "R&D (Semiconductor)", "Supply Chain (Semiconductor)"]
    },
    "ASML Holding": {
        "description": "A Dutch multinational corporation specializing in the development and manufacturing of photolithography systems for the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Photolithography", "EUV Lithography", "Advanced Manufacturing", "Optics", "Precision Engineering", "Vacuum Technology", "Cleanroom Technology", "High-Tech Manufacturing"]
    },
    "Micron Technology": {
        "description": "An American producer of computer memory and computer data storage including DRAM, NAND flash, and NOR flash.",
        "keywords": ["Semiconductors", "Memory (DRAM, NAND)", "Flash Storage", "Solid State Drives (SSDs)", "Memory Controllers", "Chip Design", "Manufacturing (Memory)", "Data Storage Solutions"]
    },
    "Applied Materials": {
        "description": "A global leader in materials engineering solutions for the semiconductor, flat panel display, and solar photovoltaic industries.",
        "keywords": ["Semiconductor Equipment", "Materials Science", "Process Engineering", "Thin Film Deposition", "Etch Technology", "Ion Implantation", "Metrology", "Yield Management", "Manufacturing (Semiconductor)"]
    },
    "Lam Research": {
        "description": "A global supplier of wafer fabrication equipment and services to the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Wafer Fabrication", "Etch", "Deposition", "Process Control", "Materials Engineering", "Advanced Manufacturing", "R&D (Semiconductor)"]
    },
    "Amdocs": {
        "description": "A multinational corporation that specializes in software and services for communications, media, and financial services providers.",
        "keywords": ["Telecommunications Software", "BSS/OSS", "Digital Transformation (Telecom)", "CRM (Telecom)", "Billing Systems", "Customer Experience (Telecom)", "Cloud Native (Telecom)", "5G Solutions", "Network Management"]
    },
    "Ericsson": {
        "description": "A Swedish multinational networking and telecommunications company.",
        "keywords": ["Telecommunications", "5G Networks", "Mobile Networks", "Radio Access Networks (RAN)", "Network Infrastructure", "IoT Connectivity", "Managed Services", "Network Orchestration", "Cloud Native (Telecom)"]
    },
    "Nokia": {
        "description": "A Finnish multinational telecommunications, information technology, and consumer electronics company.",
        "keywords": ["Telecommunications", "5G Networks", "Network Infrastructure", "Fixed Networks", "Cloud & Network Services", "Optical Networks", "Cybersecurity (Telecom)", "IoT", "Private Wireless Networks"]
    },
    "ZTE Corporation": {
        "description": "A Chinese multinational telecommunications equipment and systems company.",
        "keywords": ["Telecommunications Equipment", "5G Networks", "Wireless Communication", "Optical Communication", "Core Network", "IoT Solutions", "Smart City Solutions", "Network Infrastructure"]
    },
    "SoftBank Group": {
        "description": "A Japanese multinational conglomerate holding company primarily focused on investment in technology, energy, and financial companies.",
        "keywords": ["Investment (Tech)", "Venture Capital", "Vision Fund", "AI Investment", "Telecommunications (SoftBank Corp.)", "ARM Holdings", "Robotics (Boston Dynamics)", "Disruptive Technologies"]
    },
    "Tencent": {
        "description": "A Chinese multinational technology and entertainment conglomerate holding company.",
        "keywords": ["Gaming (Tencent Games)", "Social Media (WeChat)", "FinTech (WeChat Pay)", "Cloud Computing (Tencent Cloud)", "AI", "Content Platforms", "Digital Entertainment", "E-commerce", "Online Advertising"]
    },
    "Alibaba Group": {
        "description": "A Chinese multinational technology company specializing in e-commerce, retail, Internet, and technology.",
        "keywords": ["E-commerce (Taobao, Tmall)", "FinTech (Ant Group, Alipay)", "Cloud Computing (Alibaba Cloud)", "Logistics (Cainiao)", "Digital Media & Entertainment", "AI", "Big Data", "Supply Chain", "Retail Tech"]
    },
    "ByteDance": {
        "description": "A Chinese internet technology company, best known for its video-sharing platform TikTok.",
        "keywords": ["Social Media", "Short-form Video (TikTok)", "Content Recommendation", "AI (Recommendation Algorithms)", "Machine Learning", "Natural Language Processing (NLP)", "Computer Vision", "Content Creation Tools", "AdTech", "Global Scale"]
    },
    "Baidu": {
        "description": "A Chinese multinational technology company specializing in internet-related services and products, and artificial intelligence.",
        "keywords": ["Search Engine", "AI", "Autonomous Driving (Apollo)", "Cloud Computing (Baidu AI Cloud)", "Natural Language Processing (NLP)", "Computer Vision", "Smart Devices", "Digital Assistant (DuerOS)", "Machine Learning", "Big Data"]
    },
    # More Indian Tech Companies (Established & Emerging)
    "Zerodha": {
        "description": "India's largest retail stockbroker, offering a flat-fee brokerage model.",
        "keywords": ["FinTech", "Stock Trading", "Investment Platform", "Brokerage", "Mobile App Development", "Data Analytics (Finance)", "Algorithmic Trading", "Frontend Development", "Backend Development", "Scalability", "Security (Financial)"]
    },
    "Groww": {
        "description": "An Indian online investment platform for mutual funds and stocks.",
        "keywords": ["FinTech", "Investment Platform", "Mutual Funds", "Stock Trading", "User Experience (UX)", "Mobile App Development", "Data Analytics", "Personal Finance", "Wealth Management"]
    },
    "ShareChat": {
        "description": "An Indian social media and short video platform available in multiple Indian languages.",
        "keywords": ["Social Media", "Short-form Video", "Content Recommendation", "AI (Content)", "Machine Learning", "Natural Language Processing (NLP)", "Mobile App Development", "Vernacular Content", "User Engagement", "AdTech"]
    },
    "Dailyhunt": {
        "description": "An Indian content and news aggregator platform, providing local language content.",
        "keywords": ["Content Aggregation", "News Platform", "Local Language Content", "AI (Content Recommendation)", "Natural Language Processing (NLP)", "Mobile App Development", "AdTech", "User Engagement", "Big Data"]
    },
    "Dreamplug (formerly CRED's parent company)": {
        "description": "Parent company of CRED, focusing on financial technology and consumer products.",
        "keywords": ["FinTech", "Consumer Tech", "Financial Products", "Digital Payments", "Data Analytics", "Product Management", "Mobile Development", "Strategy", "User Experience (UX)"]
    },
    "Pine Labs": {
        "description": "An Indian merchant commerce platform providing payment solutions and financial services.",
        "keywords": ["FinTech", "Payment Solutions", "POS Systems", "Merchant Services", "Digital Payments", "Installment Payments", "Credit", "SME Solutions", "API Integration", "Cloud Payments"]
    },
    "IndusInd Bank": {
        "description": "A leading private sector bank in India, focusing on digital banking initiatives.",
        "keywords": ["FinTech", "Digital Banking", "Core Banking Systems", "Mobile Banking", "Cybersecurity (Banking)", "Data Analytics (Financial)", "Risk Management", "Blockchain (Financial Services)", "Retail Banking", "Corporate Banking"]
    },
    "HDFC Bank": {
        "description": "India's largest private sector bank, rapidly adopting digital technologies.",
        "keywords": ["FinTech", "Digital Banking", "Mobile Banking", "Core Banking", "Payments", "Cybersecurity (Banking)", "Data Analytics (Financial)", "AI in Banking", "Fraud Detection", "Risk Management"]
    },
    "ICICI Bank": {
        "description": "A major Indian multinational banking and financial services company, leveraging technology for customer experience.",
        "keywords": ["FinTech", "Digital Banking", "Mobile Banking", "Payments", "AI in Banking", "Blockchain (Financial)", "Cybersecurity (Banking)", "Data Analytics", "Customer Experience", "Retail Banking", "Corporate Banking"]
    },
    "Airtel Digital": {
        "description": "The digital arm of Bharti Airtel, focusing on digital services and products.",
        "keywords": ["Digital Services", "Telecommunications", "Mobile Payments (Airtel Payments Bank)", "Content Streaming (Airtel Xstream)", "AdTech", "Gaming", "Cybersecurity", "Cloud Services", "Data Analytics", "5G applications"]
    },
    "Nazara Technologies": {
        "description": "An Indian gaming and sports media company.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "OYO Rooms": {
        "description": "An Indian multinational hospitality chain of leased and franchised hotels, homes, and living spaces.",
        "keywords": ["Hospitality Tech", "Travel Tech", "Platform Development", "Supply Chain (Hospitality)", "Revenue Management", "Mobile App Development", "User Experience (UX)", "Data Analytics", "Hyperlocal"]
    },
    "MakeMyTrip": {
        "description": "An Indian online travel company providing travel services and products.",
        "keywords": ["Travel Tech", "Online Travel Agency (OTA)", "Flight Booking", "Hotel Booking", "Holiday Packages", "Mobile App Development", "E-commerce", "Payment Gateways", "Recommendation Systems"]
    },
    "EaseMyTrip": {
        "description": "An Indian online travel company offering flight, hotel, and holiday bookings.",
        "keywords": ["Travel Tech", "Online Travel Agency (OTA)", "Flight Booking", "Hotel Booking", "Bus Booking", "Rail Booking", "E-commerce", "Payment Gateways", "User Experience (UX)"]
    },
    "CarDekho": {
        "description": "An Indian automotive platform providing information and services related to new and used cars.",
        "keywords": ["Automotive Tech", "Online Marketplace (Cars)", "Digital Marketing", "Lead Generation", "Data Analytics (Automotive)", "AI (Pricing)", "Customer Experience", "Mobile App Development"]
    },
    "Spinny": {
        "description": "An Indian used car retailing platform focusing on transparency and quality.",
        "keywords": ["Automotive Tech", "Used Car Market", "E-commerce", "Logistics (Automotive)", "Quality Assurance", "Data Analytics", "Customer Experience", "Blockchain (Supply Chain)"]
    },
    "PharmEasy": {
        "description": "An Indian online pharmacy and healthcare aggregator.",
        "keywords": ["HealthTech", "E-pharmacy", "Online Diagnostics", "Telemedicine", "Supply Chain (Pharma)", "Logistics", "Mobile App Development", "Data Analytics (Healthcare)", "Personalized Healthcare"]
    },
    "Apollo Hospitals": {
        "description": "One of India's largest healthcare groups, also venturing into digital health.",
        "keywords": ["HealthTech", "Hospital Management Systems (HMS)", "Telemedicine", "Digital Health Records (EHR)", "AI in Healthcare", "Medical Imaging", "Data Analytics (Clinical)", "Patient Engagement Platforms", "IoT (Medical Devices)"]
    },
    "Max Healthcare": {
        "description": "A leading chain of hospitals in India, adopting digital transformation in healthcare delivery.",
        "keywords": ["HealthTech", "Hospital Information Systems (HIS)", "Digital Health", "Teleconsultation", "AI in Diagnostics", "Data Analytics (Healthcare Operations)", "Patient Portals", "Medical IoT"]
    },
    "Innovaccer": {
        "description": "A healthcare technology company unifying patient data and providing actionable insights.",
        "keywords": ["HealthTech", "Data Platform (Healthcare)", "Population Health Management", "AI in Healthcare", "Machine Learning (Clinical)", "Interoperability", "Data Governance (Healthcare)", "Value-Based Care", "Cloud Computing"]
    },
    "Practo": {
        "description": "An Indian healthcare technology company connecting patients with doctors and clinics online.",
        "keywords": ["HealthTech", "Telemedicine", "Online Doctor Consultation", "Appointment Booking", "EHR (Electronic Health Records)", "Practice Management Software", "Mobile App Development", "Data Analytics (Healthcare)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "BharatPe": {
        "description": "An Indian FinTech company offering QR code-based payment solutions and financial services to merchants.",
        "keywords": ["FinTech", "Digital Payments", "QR Code Payments", "Merchant Solutions", "SME Lending", "UPI", "Data Analytics (Merchant)", "Fraud Detection", "Mobile App Development"]
    },
    "Open Financial Technologies": {
        "description": "Asia's first neo-banking platform for SMEs and startups.",
        "keywords": ["FinTech", "Neo-banking", "SME Banking", "Payments API", "Expense Management", "Payroll Automation", "Cloud Banking", "API Integrations", "Cybersecurity (FinTech)", "Financial Automation"]
    },
    "Jupiter Money": {
        "description": "An Indian neo-banking platform providing a digital-first banking experience.",
        "keywords": ["FinTech", "Neo-banking", "Digital Banking", "Mobile Banking", "Personal Finance", "Wealth Management", "Payments", "User Experience (UX)", "Data Analytics"]
    },
    "CoinDCX": {
        "description": "An Indian cryptocurrency exchange and crypto investment platform.",
        "keywords": ["FinTech", "Cryptocurrency", "Blockchain", "Crypto Exchange", "Decentralized Finance (DeFi)", "Trading Platforms", "Cybersecurity (Crypto)", "Risk Management", "Backend Development", "Scalability"]
    },
    "CoinSwitch Kuber": {
        "description": "An Indian cryptocurrency exchange platform for simplified crypto investments.",
        "keywords": ["FinTech", "Cryptocurrency", "Blockchain", "Crypto Investment", "Mobile App Development", "User Experience (UX)", "Security (Crypto)", "Data Analytics", "Trading Algorithms"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Infibeam Avenues": {
        "description": "An Indian e-commerce and payment solutions company.",
        "keywords": ["E-commerce Platform", "Payment Gateway (CCAvenue)", "FinTech", "Online Retail Solutions", "Digital Payments", "White-label Solutions", "Cloud Computing"]
    },
    "MapmyIndia (CE Info Systems)": {
        "description": "An Indian company specializing in digital maps, geospatial software, and location-based IoT technologies.",
        "keywords": ["Mapping Technology", "GIS (Geographic Information Systems)", "Location-based Services", "IoT", "Navigation Systems", "GPS", "Data Analytics (Geospatial)", "Autonomous Vehicles (Mapping)", "Smart Cities"]
    },
    "Happiest Minds Technologies": {
        "description": "An Indian IT services company focusing on digital transformation, cloud, and cybersecurity.",
        "keywords": ["Digital Transformation", "Cloud Services", "Cybersecurity", "IoT", "AI & Analytics", "Product Engineering", "Infrastructure Management", "Automation", "DevOps", "Agile", "Enterprise Solutions"]
    },
    "Coforge": {
        "description": "A global IT solutions organization enabling businesses to transform with digital technologies.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Automation", "Cybersecurity", "Application Development", "Microservices", "API Management", "Travel Tech", "Financial Services"]
    },
    "Mindtree (now LTIMindtree)": {
        "description": "A global technology consulting and services company, now part of LTIMindtree.",
        "keywords": ["Digital Transformation", "Cloud Solutions", "Data & AI", "Enterprise Applications", "Product Engineering", "Customer Experience (CX)", "Agile Development", "DevOps", "IoT", "Managed Services"]
    },
    "Genpact": {
        "description": "A global professional services firm focused on delivering digital transformation and business process management.",
        "keywords": ["Digital Transformation", "Business Process Management (BPM)", "AI & Automation", "Data Analytics", "Financial Services Operations", "Supply Chain Management", "Risk & Compliance", "Robotics Process Automation (RPA)", "Consulting"]
    },
    "EXL Service": {
        "description": "A global analytics and digital operations and solutions company.",
        "keywords": ["Data Analytics", "AI", "Machine Learning", "Digital Operations", "Business Process Outsourcing (BPO)", "Risk Management", "Customer Experience (CX)", "Healthcare Analytics", "Insurance Analytics", "Financial Services Analytics"]
    },
    "WNS (Holdings)": {
        "description": "A global business process management (BPM) company.",
        "keywords": ["Business Process Management (BPM)", "Digital Transformation", "Automation", "Analytics", "Customer Experience (CX)", "Travel BPM", "Healthcare BPM", "Finance & Accounting BPM", "Robotics Process Automation (RPA)"]
    },
    "KPIT Technologies": {
        "description": "An Indian multinational corporation that provides software to the automotive industry.",
        "keywords": ["Automotive Software", "Autonomous Driving", "Electric Vehicles (EV)", "Connected Cars", "Infotainment Systems", "Embedded Systems", "Software-Defined Vehicles (SDV)", "AI (Automotive)", "ADAS (Advanced Driver-Assistance Systems)", "Vehicle Diagnostics"]
    },
    "Tata Motors": {
        "description": "An Indian multinational automotive manufacturing company, increasingly focused on electric vehicles and connected car technologies.",
        "keywords": ["Automotive Manufacturing", "Electric Vehicles (EV)", "Connected Car Technology", "ADAS", "Software Engineering (Automotive)", "Battery Management Systems (BMS)", "Infotainment", "IoT (Automotive)", "Supply Chain (Automotive)"]
    },
    "Mahindra & Mahindra": {
        "description": "An Indian multinational automotive manufacturing corporation, with a focus on SUVs, commercial vehicles, and electric mobility.",
        "keywords": ["Automotive Manufacturing", "Electric Vehicles (EV)", "Farm Equipment (Tech)", "Connected Vehicles", "ADAS", "Software Engineering (Automotive)", "IoT (Automotive)", "Sustainable Mobility"]
    },
    "Bajaj Auto": {
        "description": "An Indian multinational two-wheeler and three-wheeler manufacturing company, exploring electric and smart mobility solutions.",
        "keywords": ["Automotive Manufacturing", "Electric Two/Three Wheelers", "Connected Mobility", "IoT (Vehicles)", "Powertrain Technology", "Software Engineering (Embedded)"]
    },
    "Ather Energy": {
        "description": "An Indian electric scooter manufacturer and charging infrastructure provider.",
        "keywords": ["Electric Vehicles (EV)", "Electric Scooters", "Battery Technology", "IoT (Connected Vehicles)", "Charging Infrastructure", "Mobile App Development (EV)", "Embedded Systems", "Hardware Engineering (EV)"]
    },
    "Rebel Foods": {
        "description": "An Indian online restaurant company, operating multiple cloud kitchen brands.",
        "keywords": ["Cloud Kitchen", "Food Tech", "Restaurant Tech", "Logistics", "Supply Chain (Food)", "Data Analytics (Food Delivery)", "AI (Demand Forecasting)", "Brand Management", "Ghost Kitchens"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Zomato": {
        "description": "An Indian multinational restaurant aggregator and food delivery company.",
        "keywords": ["Food Delivery", "Restaurant Technology", "Logistics", "Mobile Development", "Data Analytics", "Machine Learning (Recommendation Systems)", "Cloud Infrastructure", "Geolocation", "Payment Gateways", "User Experience (UX)", "Growth Hacking"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Urban Company": {
        "description": "An Indian at-home services platform.",
        "keywords": ["On-demand Services", "Hyperlocal", "Mobile App Development", "Logistics", "Geolocation", "Service Marketplace", "User Experience (UX)", "Payment Systems"]
    },
    "Vedantu": {
        "description": "An Indian online tutoring platform providing live interactive classes.",
        "keywords": ["EdTech", "Online Tutoring", "Live Classes", "Personalized Learning", "Mobile App Development", "Learning Management Systems (LMS)", "AI (Learning Analytics)", "Gamification"]
    },
    "Unacademy": {
        "description": "An Indian online education technology company.",
        "keywords": ["EdTech", "Online Learning", "Live Classes", "Test Preparation", "Content Creation", "Mobile App Development", "Data Analytics (Learning)", "Personalized Learning"]
    },
    "Toppr (Byju's Group)": {
        "description": "An Indian online learning platform for K-12 and competitive exams.",
        "keywords": ["EdTech", "Online Learning", "Test Preparation", "Content Creation", "Adaptive Learning", "AI (Personalized Study)", "Mobile App Development", "Gamification"]
    },
    "BYJU'S": {
        "description": "An Indian multinational educational technology company, providing online tutoring and learning programs.",
        "keywords": ["EdTech", "Online Learning", "Content Creation (Video, Animation)", "Mobile App Development", "AI (Personalized Learning)", "Machine Learning", "Data Analytics (Student Progress)", "Curriculum Development", "User Experience", "Subscription Models"]
    },
    "UpGrad": {
        "description": "An Indian online higher education company providing online programs.",
        "keywords": ["EdTech", "Online Higher Education", "Skill Development", "Career Services", "Content Curation", "Learning Management Systems (LMS)", "Data Analytics (Career Outcomes)", "Industry Partnerships"]
    },
    "Great Learning": {
        "description": "An Indian ed-tech company providing online professional and higher education programs.",
        "keywords": ["EdTech", "Professional Education", "Upskilling", "Data Science Courses", "AI Courses", "Cloud Computing Courses", "Career Development", "Online Learning Platform"]
    },
    "Druva": {
        "description": "A cloud data protection and management company.",
        "keywords": ["Cloud Data Protection", "Data Backup", "Disaster Recovery", "Data Governance", "Cybersecurity", "SaaS", "Cloud Computing", "Data Resilience", "Compliance", "Security Automation"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "Mobikwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": { # Duplicate with slightly different description for clarity if needed
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    }
}

# Convert all company keywords to lowercase for consistent matching
for company_data in COMPANY_SKILL_PROFILES.values():
    company_data["keywords"] = [kw.lower() for kw in company_data["keywords"]]
