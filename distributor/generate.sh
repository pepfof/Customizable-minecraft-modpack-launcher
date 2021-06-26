find . -type f > mine.txt &
find . -type d > dirs.txt 
sed -i 's \./ \\ g' mine.txt 
sed -i 's / \\ g' mine.txt  
sed -i 's \./ \\ g' dirs.txt 
sed -i 's / \\ g' dirs.txt
touch remv.txt
