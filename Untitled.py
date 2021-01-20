# {
#  "cells": [
#   {
#    "cell_type": "code",
#    "execution_count": 36,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "import numpy\n",
#     "import sqlite3"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 84,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "db = sqlite3.connect(\"RAW_recipes.db\")\n",
#     "curs = db.cursor()"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 85,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "ib_list = curs.execute(\"SELECT ingredients FROM CookHub\").fetchall()\n",
#     "ib_list2 = curs.execute(\"SELECT tags FROM CookHub\").fetchall()"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 86,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "z = []\n",
#     "for i in ib_list:\n",
#     "    for j in i:\n",
#     "        for h in j[1:-1].split(\",\"):\n",
#     "            h = h.strip(\"'\")\n",
#     "#                 print(h[0], h[1], h[2], h[3])\n",
#     "            if h[0]  == \" \":\n",
#     "                h = h[2:]\n",
#     "            if h not in z:\n",
#     "                z.append(h)\n",
#     "z2 = []\n",
#     "for i in ib_list2:\n",
#     "    for j in i:\n",
#     "        for h in j[1:-1].split(\",\"):\n",
#     "            h = h.strip(\"'\")\n",
#     "            if h[0]  == \" \":\n",
#     "                h = h[2:]\n",
#     "            if h not in z2:\n",
#     "                z2.append(h)\n",
#     "#             if h not in z2:\n",
#     "#                 z2.append(h.strip(\"''\"))"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 87,
#    "metadata": {},
#    "outputs": [
#     {
#      "name": "stdout",
#      "output_type": "stream",
#      "text": [
#       "beverages\n"
#      ]
#     }
#    ],
#    "source": [
#     "print(z2[60])"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 88,
#    "metadata": {},
#    "outputs": [
#     {
#      "data": {
#       "text/plain": [
#        "<sqlite3.Cursor at 0x57c5d50>"
#       ]
#      },
#      "execution_count": 88,
#      "metadata": {},
#      "output_type": "execute_result"
#     }
#    ],
#    "source": [
#     "curs.execute(\"CREATE TABLE UNIQUES(ingredients TEXT, tags TEXT)\")"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 89,
#    "metadata": {},
#    "outputs": [
#     {
#      "data": {
#       "text/plain": [
#        "<sqlite3.Cursor at 0x57c5d50>"
#       ]
#      },
#      "execution_count": 89,
#      "metadata": {},
#      "output_type": "execute_result"
#     }
#    ],
#    "source": [
#     "curs.execute(\"INSERT INTO Uniques Values (?, ?)\", (str(z), str(z2)))"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": 90,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "db.commit()\n",
#     "curs.close()"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": []
#   }
#  ],
#  "metadata": {
#   "kernelspec": {
#    "display_name": "Python 3",
#    "language": "python",
#    "name": "python3"
#   },
#   "language_info": {
#    "codemirror_mode": {
#     "name": "ipython",
#     "version": 3
#    },
#    "file_extension": ".py",
#    "mimetype": "text/x-python",
#    "name": "python",
#    "nnbconvert_exporter": "python",
#    "pygments_lexer": "ipython3",
#    "version": "3.7.1"
#   }
#  },
#  "nbformat": 4,
#  "nbformat_minor": 2
# }
import sqlite3
db = sqlite3.connect("RAW_recipes.db")
curs = db.cursor()
curs.execute("DELETE FROM CookHub WHERE description IS NULL")
db.commit()
curs.close()