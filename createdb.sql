create table Users
            (ID numeric(19,0) unique primary key
            ,Brief varchar(50)
            );
create table Chats
            (ID numeric(19,0) unique primary key);
create table Operation
            (ID    numeric(19,0) identity unique primary key
            ,UFrom numeric(19,0) 
            ,UTo   numeric(19,0)
            ,Qty   money
            ,ChatID numeric(19,0)
            ,FOREIGN KEY (UFrom)  references  Users(ID)
            ,FOREIGN KEY (UTo)    references  Users(ID)
            ,FOREIGN KEY (ChatID) references  Chats(ID)
            );
