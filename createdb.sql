create table Users            
            (ID INTEGER  unique primary key 
            ,Brief varchar(50)
            );
            

create table Chats
            (ID integer unique primary key);

create table UserChatRelation
            (ID integer primary key autoincrement
            ,ChatID integer 
            ,UserID integer
            ,FOREIGN KEY (ChatID) references Chats(ID)
            ,FOREIGN KEY (UserID) references Users(ID));
            
create table Operation
            (ID     integer primary key autoincrement
            ,UFrom  integer 
            ,UTo    integer
            ,Qty    money
            ,ChatID integer
            ,Date   datetime
            ,Comment varchar(255)
            ,FOREIGN KEY (UFrom)  references  Users(ID)
            ,FOREIGN KEY (UTo)    references  Users(ID)
            ,FOREIGN KEY (ChatID) references  Chats(ID)
            );

create table Operations
            (ID     integer primary key autoincrement
            ,UserFrom  integer 
            ,UserTo    varchar(255)
            ,Qty    money
            ,ChatID integer
            ,Comment varchar(255)
            ,Type integer
            ,FOREIGN KEY (UserFrom)  references  Users(ID)            
            ,FOREIGN KEY (ChatID) references  Chats(ID)
            );
