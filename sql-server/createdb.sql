create DATABASE if not exists veksel;
use veksel;
create table if not exists Users            
            (ID INTEGER  unique primary key 
            ,Brief varchar(50)
            );
            

create table if not exists Chats
            (ID integer unique primary key);

create table if not exists UserChatRelation
            (ID integer primary key autoincrement
            ,ChatID integer 
            ,UserID integer
            ,FOREIGN KEY (ChatID) references Chats(ID)
            ,FOREIGN KEY (UserID) references Users(ID));
            
create table if not exists Operation
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

create table if not exists Operations
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
