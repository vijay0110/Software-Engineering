INSERT INTO user (email, nickname, password, joke_balance, is_mod)
VALUES
  ('testuser@gmail.com', 'testuser', 'scrypt:32768:8:1$Ylf5O7LyLmgLxTTi$102aac69de1e3a1f845f272bddf72685e051350174cc2a6af163537ab3967b653d5bdecb38942066dcd3d3e98ec08054bff69e294d797068ac1bb7e4dbcb44ef', 0, FALSE),
  ('testmoderator@gmail.com', 'testmoderator', 'scrypt:32768:8:1$Ylf5O7LyLmgLxTTi$102aac69de1e3a1f845f272bddf72685e051350174cc2a6af163537ab3967b653d5bdecb38942066dcd3d3e98ec08054bff69e294d797068ac1bb7e4dbcb44ef', 0, TRUE);


INSERT INTO joke (title, body, author_id, author_nickname) VALUES ('A Test Joke', 'A Test Joke Body', 4, 'dummyuser')