# 🏹 Archery Management System

A comprehensive web-based platform for managing archery clubs, tournaments, and community connections in Australia. Built with Streamlit and Supabase, this system provides a complete solution for archery enthusiasts, event organizers, and club administrators.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [User Roles](#user-roles)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Pages & Functionality](#pages--functionality)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The **Archery Management System** is designed to bring together archery enthusiasts, athletes, and clubs in one digital space. The platform simplifies tournament management, score tracking, and community connections, providing a modern solution for both organizers and participants.

### Key Objectives

- **Streamline Event Management**: Register for national or local tournaments with ease
- **Club Management**: Explore, join, and manage official archery clubs
- **Social Networking**: Build friendships and connections with other archers
- **Performance Tracking**: Track shooting scores, view historical performance, and compare results
- **Community Building**: Foster a vibrant and supportive archery community

## ✨ Features

### For Archers
- 📊 **Score Tracking**: Record and monitor competition and practice scores
- 🏆 **Performance Analysis**: View rankings, percentiles, and normalized scores
- 🎯 **Event Registration**: Browse and register for competitions and championships
- 👥 **Social Features**: Connect with other archers, send friend requests, and chat
- 🏛️ **Club Management**: Create or join archery clubs

### For Recorders
- 📝 **Event Creation**: Design and structure yearly championships and club competitions
- ⚙️ **Competition Configuration**: Configure rounds, ranges, and ends for events
- 👥 **Participant Management**: Accept/reject participant and recorder applications
- 🗓️ **Scheduling**: Schedule rounds for club competitions
- ✅ **Score Verification**: Verify and validate participant scores

### For AAF Members
- 🎯 **Equipment Management**: Add new equipment, disciplines, and age divisions
- 📏 **Round Configuration**: Create new rounds and ranges
- 🎨 **Target Face Setup**: Add new target face specifications
- 🔄 **Round Equivalence**: Define equivalent rounds across categories

### For Administrators
- 👤 **Account Management**: Add, modify, activate, and deactivate user accounts
- 📊 **Dashboard Analytics**: Monitor system statistics and user metrics
- 🚨 **Report Management**: Review and act on account reports
- 🔒 **Security**: Manage user permissions and access control

### Additional Features
- 🤖 **AI Chatbot Assistant**: GPT-like interface for database queries and support
- 💬 **Messaging System**: Direct messaging and group chat functionality
- 🔍 **Advanced Search**: Search and filter accounts, clubs, and events
- 📈 **Analytics**: Comprehensive performance metrics and statistics

## 🏗️ System Architecture

```
┌─────────────────┐
│   Streamlit UI  │
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Backend │
│  (Business Logic)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Supabase     │
│  (PostgreSQL DB)│
└─────────────────┘
```

### Technology Stack

- **Frontend**: Streamlit (Python-based web framework)
- **Backend**: Python 3.x
- **Database**: Supabase (PostgreSQL)
- **AI Integration**: Google Generative AI (Gemini)
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage (for images and files)

## 👥 User Roles

### 1. Admin
- Manage user accounts (add, modify, activate, deactivate)
- Review and act on account reports
- Monitor system-wide statistics
- **Access**: Contact DB team to become an admin

### 2. AAF Member (Australian Archery Federation)
- Add new rounds, ranges, and target faces
- Define disciplines, age divisions, and equipment types
- Set round equivalence relationships
- **Access**: Contact DB team to become an AAF member

### 3. Recorder
- Create yearly club championships and club competitions
- Design event structure (rounds, ranges, ends)
- Accept/reject participant and recorder applications
- Schedule competitions and manage participants
- Verify participant scores
- **Access**: Select "recorder" role during sign-up

### 4. Archer
- Register for competitions and championships
- Record competition and practice scores
- View personal and community performance
- Create or join one archery club
- Connect with other archers
- **Access**: Select "archer" role during sign-up

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Supabase account (for database setup)

### Step-by-Step Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/Jack9671/Archery-Managment-Application.git
   cd Archery-Managment-Application
   ```

2. **Create a virtual environment**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   GOOGLE_API_KEY=your_google_ai_api_key
   ```

6. **Set up the database**
   
   Run the SQL scripts in the following order:
   ```powershell
   # 1. Create database schema
   # Execute: sql_documentation/Archery ERD.sql
   
   # 2. Insert sample data
   # Execute: sql_documentation/SAMPLE_DATA.sql
   
   # 3. Set up permissions
   # Execute: sql_documentation/SET_PERMISSION_FOR_API.sql
   
   # 4. Configure Row Level Security
   # Execute: sql_documentation/RLS_POLICY.sql
   ```

7. **Run the application**
   ```powershell
   streamlit run main.py
   ```

8. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous/public key | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (admin access) | Yes |
| `GOOGLE_API_KEY` | Google Generative AI API key for chatbot | Yes |

### Database Configuration

The system uses PostgreSQL via Supabase with the following features:
- Row Level Security (RLS) for data protection
- Custom user permissions based on roles
- Automated triggers for data validation
- Comprehensive foreign key relationships

## 📖 Usage

### For First-Time Users

1. **Sign Up**
   - Navigate to the Sign Up/Log In page
   - Choose your role (Archer or Recorder)
   - Fill in required information
   - Create your account

2. **Log In**
   - Use your email and password to log in
   - You'll be redirected to the main dashboard

3. **Explore Features**
   - Browse events in the Event page
   - Join a club in the Club page
   - Track your performance in the Performance page
   - Connect with other archers in My Connection page

### For Archers

1. **Join a Club**
   - Navigate to Club page
   - Browse available clubs
   - Submit club enrollment request
   - Wait for club creator approval

2. **Register for Competition**
   - Go to Event page
   - Browse available competitions
   - Submit competition request form
   - Track your registration status

3. **Record Scores**
   - Navigate to Score Tracking page
   - Select your event and round
   - Enter arrow-by-arrow scores
   - Submit for verification

### For Recorders

1. **Create a Competition**
   - Navigate to Event page
   - Click "Create New Competition"
   - Configure rounds, ranges, and ends
   - Set eligibility criteria
   - Publish the event

2. **Manage Participants**
   - Review participant applications
   - Accept or reject requests
   - Monitor participant scores
   - Verify submitted scores

## 📁 Project Structure

```
Archery-Management-Application/
│
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in git)
├── .gitignore                   # Git ignore file
├── project_description.txt      # Detailed project documentation
│
├── pages/                       # Streamlit pages
│   ├── Admin.py                 # Admin dashboard
│   ├── Category.py              # Category management
│   ├── Chatbot_Assistant.py     # AI chatbot interface
│   ├── Club.py                  # Club management
│   ├── Event.py                 # Event management
│   ├── My_Connection.py         # Social connections
│   ├── My_Friend_Request.py     # Friend requests
│   ├── Performance.py           # Performance tracking
│   ├── Score_Tracking.py        # Score entry/tracking
│   └── Sign_Up_Log _in.py       # Authentication
│
├── utility_function/            # Helper functions
│   ├── __init__.py
│   ├── admin_utility.py         # Admin operations
│   ├── category_utility.py      # Category operations
│   ├── club_utility.py          # Club operations
│   ├── event_utility.py         # Event operations
│   ├── initilize_dbconnection.py # Database connection
│   ├── my_connection_utility.py # Social features
│   ├── my_friend_request_utility.py # Friend requests
│   ├── performance_utility.py   # Performance analytics
│   ├── score_tracking_utility.py # Score operations
│   └── sign_up_log_in_utility.py # Authentication
│
├── sql_documentation/           # Database scripts
│   ├── Archery ERD.sql          # Database schema
│   ├── SAMPLE_DATA.sql          # Sample data
│   ├── SET_PERMISSION_FOR_API.sql # API permissions
│   └── RLS_POLICY.sql           # Row Level Security
│
├── components/                  # Reusable UI components
├── images/                      # Static images
├── pdfs/                        # PDF documents
└── posters/                     # Event posters
```

## 🗄️ Database Schema

### Core Tables

#### Account Management
- `account` - User accounts and authentication
- `admin` - Administrator accounts
- `archer` - Archer profiles
- `recorder` - Recorder profiles
- `australia_archery_federation` - AAF member profiles

#### Event Management
- `yearly_club_championship` - Annual championships
- `club_competition` - Individual competitions
- `round` - Competition rounds
- `range` - Distance and target specifications
- `event_context` - End-by-end score records

#### Club Management
- `club` - Archery clubs
- `club_enrollment` - Club membership requests
- `club_member` - Club membership records

#### Category System
- `category` - Round categories
- `discipline` - Archery disciplines
- `age_division` - Age categories
- `equipment` - Equipment types
- `target_face` - Target specifications

#### Social Features
- `friend_connection` - Friend relationships
- `friend_request` - Friend request management
- `private_conversation` - Direct messages
- `club_chat_message` - Group chat messages

#### Performance Tracking
- `participant_score` - Individual scores
- `category_rating_percentile` - Performance rankings
- `competition_request_form` - Event registrations

### Key Relationships

```sql
account (1) --> (0..1) admin
account (1) --> (0..1) archer
account (1) --> (0..1) recorder
account (1) --> (0..1) australia_archery_federation

archer (1) --> (0..1) club_member
club (1) --> (0..*) club_member

yearly_club_championship (1) --> (1..*) club_competition
club_competition (1) --> (1..*) event_context
round (1) --> (1..*) event_context
range (1) --> (1..*) event_context

archer (1) --> (0..*) participant_score
event_context (1) --> (0..*) participant_score
```

## 📱 Pages & Functionality

### 1. Sign Up / Log In
- User registration with role selection
- Email and password authentication
- Profile creation

### 2. Admin Dashboard
- Account management (add, modify, deactivate)
- Account report review
- System statistics and analytics
- User sorting and filtering

### 3. Event Page
- Browse yearly championships and competitions
- View event details (rounds, ranges, ends)
- Submit participant/recorder request forms
- Track registration status

### 4. Score Tracking
- Enter arrow-by-arrow scores
- Submit competition and practice scores
- View and verify scores (for recorders)
- Edit unverified scores

### 5. Performance Page
- View personal performance metrics
- Compare scores with other participants
- Analyze performance by category
- View rankings and percentiles
- Track normalized average scores

### 6. Category Page
- Browse equipment types
- View discipline descriptions
- Explore age divisions
- Add new options (AAF members only)

### 7. Club Page
- Browse and search clubs
- Create new clubs
- Submit enrollment requests
- Manage club members (for creators)
- View club information

### 8. Chatbot Assistant
- AI-powered query interface
- Context-aware responses based on user role
- Multiple conversation support
- Database querying assistance

### 9. My Connection
- Search all users
- Filter by role or friends
- Send friend requests with messages
- Direct messaging
- Block/unblock users

### 10. My Friend Request
- View sent friend requests
- View received friend requests
- Accept or reject requests
- Track request status

## 🛠️ Development

### Adding New Features

1. **Create a new page**
   ```python
   # pages/New_Feature.py
   import streamlit as st
   from utility_function.initilize_dbconnection import supabase
   
   st.title("New Feature")
   # Your code here
   ```

2. **Add utility functions**
   ```python
   # utility_function/new_feature_utility.py
   def new_function():
       # Implementation
       pass
   ```

3. **Update database schema** (if needed)
   - Modify `sql_documentation/Archery ERD.sql`
   - Update RLS policies
   - Run migrations

### Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Comment complex logic

### Testing

```powershell
# Run the application in development mode
streamlit run main.py --server.runOnSave true
```

### Database Migrations

When making schema changes:
1. Update the ERD SQL file
2. Test changes in development environment
3. Update RLS policies if needed
4. Document changes in commit message

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Write clear commit messages
- Test your changes thoroughly
- Update documentation as needed
- Follow existing code style
- Add comments for complex logic

## 📝 Terminology Reference

- **Event**: A general term for yearly club championship or club competition
- **AAF**: Australian Archery Federation
- **Yearly Club Championship**: Event composed of multiple club competitions
- **Club Competition**: Event with 2+ rounds to compete
- **Round**: Category-specific competition where participants compete and get ranked
- **Range**: Specifies distance and target face diameter
- **End**: Record of scores from 1st to 6th arrow
- **Category**: Combination of discipline, age division, and equipment
- **Equivalent Round**: Rounds sharing the same category_id and valid date range

### Score Calculation

**Normalized Score Formula:**
```
A = B / C

Where:
A = Normalized score
B = Actual score attained from a round
C = Maximum possible score (arrows × 10)

Example: B = 180, C = 360 → A = 0.5 (50%)
```

## 🔒 Security

- Row Level Security (RLS) enabled on all tables
- Role-based access control
- Secure password hashing
- Environment variable protection
- SQL injection prevention via parameterized queries

## 📊 Performance Optimization

- Efficient database queries with proper indexing
- Lazy loading for large datasets
- Caching for frequently accessed data
- Optimized image loading

## 🐛 Troubleshooting

### Common Issues

1. **Database connection error**
   - Check `.env` file configuration
   - Verify Supabase credentials
   - Ensure network connectivity

2. **Import errors**
   - Activate virtual environment
   - Reinstall requirements: `pip install -r requirements.txt`

3. **Permission denied errors**
   - Check RLS policies in database
   - Verify user role and permissions

4. **Streamlit not starting**
   - Check if port 8501 is available
   - Try running on different port: `streamlit run main.py --server.port 8502`

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Contact the development team
- Check the project documentation

## 👨‍💻 Authors

- **Jack9671** - [GitHub Profile](https://github.com/Jack9671)

## 🙏 Acknowledgments

- Australian Archery Federation for domain expertise
- Supabase for backend infrastructure
- Streamlit for the web framework
- Google for AI capabilities

## 📜 License

This project is part of a Database Design course project. All rights reserved.

---

**Last Updated**: November 21, 2025

**Version**: 1.0.0

Made with ❤️ for the archery community
