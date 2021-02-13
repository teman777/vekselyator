create table Users            
            (ID INTEGER  unique primary key 
            ,Brief varchar(50)
            );
            

create table Chats
            (ID integer unique primary key);

create table UserChatRelation
            (ID integer unique primary key autoincrement
            ,ChatID integer 
            ,UserID integer
            ,FOREIGN KEY (ChatID) references Chats(ID)
            ,FOREIGN KEY (UserID) references Users(ID));
            
create table Operation
            (ID    integer unique primary key autoincrement
            ,UFrom integer 
            ,UTo   integer
            ,Qty   money
            ,ChatID integer
            ,FOREIGN KEY (UFrom)  references  Users(ID)
            ,FOREIGN KEY (UTo)    references  Users(ID)
            ,FOREIGN KEY (ChatID) references  Chats(ID)
            );
