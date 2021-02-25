create DATABASE if not exists veksel CHARACTER SET utf8 COLLATE utf8_general_ci;
use veksel;
create table if not exists Users            
            (ID int  unique primary key 
            ,Brief varchar(50)
            );
            

create table if not exists Chats
            (ID int unique primary key);

create table if not exists UserChatRelation
            (ID int primary key auto_increment
            ,ChatID int 
            ,UserID int
            ,FOREIGN KEY (ChatID) references Chats(ID)
            ,FOREIGN KEY (UserID) references Users(ID));
            
create table if not exists Operation
            (ID     int primary key auto_increment
            ,UFrom  int 
            ,UTo    int
            ,Qty    float
            ,ChatID int
            ,Date   datetime
            ,Comment varchar(255)
            ,FOREIGN KEY (UFrom)  references  Users(ID)
            ,FOREIGN KEY (UTo)    references  Users(ID)
            ,FOREIGN KEY (ChatID) references  Chats(ID)
            );

create table if not exists Operations
            (ID     int primary key auto_increment
            ,UserFrom  int 
            ,UserTo    varchar(255)
            ,Qty    float
            ,ChatID int
            ,Comment varchar(255)
            ,Type int
            ,FOREIGN KEY (UserFrom)  references  Users(ID)            
            ,FOREIGN KEY (ChatID) references  Chats(ID)
            );
commit;
