# You should not change this file!
# Copy your modifications into acomp/config.py
DEBUG = False                              # Flask config to run in debug mode
BCRYPT_HANDLE_LONG_PASSWORDS = True        # Flask config to handle passwords longer than 72 bytes
SQLALCHEMY_ECHO = False                    # Flask config to print SQL statements
SQLALCHEMY_TRACK_MODIFICATIONS = False     # Flask config to disable tracking of objects by
ACOMP_ALLOWED_FILE_EXT = ['.jpg', '.png']  # allowed file extensions for the prefill command
ACOMP_OBJ_DIR = "static/images"            # output directory of the prefill command
ACOMP_LIFETIME_USER = 70                   # session timeout during the game
ACOMP_LANGUAGE_DEFAULT = 'en'              # default language for user tags
ACOMP_QUIZ_POINTS = 2                      # required balance of corrent answers to pass the entry quiz
ACOMP_CLASSIC_TIMELIMIT = 30               # time limit in classic mode (in seconds)
ACOMP_CLASSIC_RATIO = 0.2                  # maximum ratio
ACOMP_CLASSIC_FORBIDDEN_TAGS = 5           # amount of tags that are shown as already mentioned
ACOMP_CAPTCHA_TIMELIMIT = 30               # time limit in captcha mode (in seconds)
ACOMP_CAPTCHA_NUM_IMAGES = 4               # number of images shhown in captcha mode
ACOMP_CAPTCHA_NUM_TAGS = 3                 # number of tags shown in captcha mode
ACOMP_NUM_HIGHSCORE = 5                    # number of users shown in the highscore
ACOMP_NUM_LEV1 = 1                         # amount of user that are needed ro reduce the score for already mentioned tags
ACOMP_NUM_LEV2 = 2                         # amount of user that are needed to mark a tag as already mentioned by others
NLTK_DATA = "/usr/share/nltk_data"         # default directory for the natural language toolkit data
