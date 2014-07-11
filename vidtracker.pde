import java.util.Map;
import processing.video.Movie;

String MOVIE_FILE = "video_file";
String OUTPUT_DIR = "pos/";
int SEEK_INTERVAL = 4;
int FAST_SEEK_INTERVAL = 100;

String OBJ_NAME = "object_name";

DisposeHandler dh;
Movie movie;
Mode mode;
Timer timer;
Tracker tracker;

void setup() {
  size(640, 480);
  dh = new DisposeHandler(this);
  movie = new Movie(this, MOVIE_FILE);
  mode = new Mode();
  timer = new Timer(movie);
  tracker = new Tracker(OBJ_NAME);
}

void draw() {
  image(movie, 0, 0, width, height);
  mode.display();
  timer.display();
  float now = movie.time();
  if (mode.recording == 1) {
    tracker.setPos(now, mouseX, mouseY);
  } else {
    Point p = tracker.getPos(now);
    if (p != null) {
      p.display();
    }
  }
}

// called every time a new frame is available to read
void movieEvent(Movie m) {
  m.read();
}

void mouseClicked() {
  if (mouseButton == LEFT) {
    togglePlay();
  } else if (mouseButton == RIGHT) {
    mode.toggle();
  }
}

void keyPressed() {
  if (keyCode == LEFT) {
    movieBakcward();
  } else if (keyCode == RIGHT) {
    movieForward();
  } else if (keyCode == UP) {
    speedUp();
  } else if (keyCode == DOWN) {
    speedDown();
  } else if (key == ' ') {
    togglePlay();
  } else if (key == 's') {
    tracker.saveCsv();
  } else if (key == 'q') {
    movieFastBackward();
  } else if (key == 'w') {
    movieFastForward();
  }
}

/////////////////////////////////////////////////////

// monkey patches instead of subclassing Movie
boolean playing = false;
float speed = 1.0F;

void togglePlay() {
  if (!playing) {
    playing = true;
    movie.play();
  } else {
    playing = false;
    movie.pause();
  }
}

void movieBakcward() {
  float now = movie.time();
  movie.jump(now - SEEK_INTERVAL);
}

void movieForward() {
  float now = movie.time();
  movie.jump(now + SEEK_INTERVAL);
}

void movieFastBackward() {
  float now = movie.time();
  movie.jump(now - FAST_SEEK_INTERVAL);
}

void movieFastForward() {
  float now = movie.time();
  movie.jump(now + FAST_SEEK_INTERVAL);
}

void speedUp() {
  speed *= 2;
  set_speed();
}

void speedDown() {
  speed *= 0.5;
  set_speed();
}

void set_speed() {
  speed = constrain(speed, 0.25, 8);
  movie.speed(speed);
}

/////////////////////////////////////////////////////

class Mode {
  int WIDTH = 100;
  int TEXT_SIZE = 18;
  int PADDING = 6;
  color[] COLORS = {color(0, 255, 0), color(255, 0, 0)};
  String[] TEXTS = {"Playing", "Recording"};
  
  int recording = 0;
  
  void toggle() {
    recording = -1 * recording + 1;
  }
  
  void display() {
    noStroke();
    fill(COLORS[recording]);
    rect(0, 0, WIDTH, TEXT_SIZE + 2 * PADDING);
    fill(0);
    textSize(TEXT_SIZE);
    text(TEXTS[recording], 0, TEXT_SIZE + PADDING);
  }
}

/////////////////////////////////////////////////////

class Timer {
  color COLOR = color(100, 100, 255, 100);
  int TEXT_SIZE = 18;
  int PADDING = 6;
  
  Movie movie;
  
  Timer(Movie movie) {
    this.movie = movie;
  }
  
  void display() {
    fill(COLOR);
    noStroke();
    rect(0, height - (TEXT_SIZE + 2 * PADDING), width, height);
    fill(0);
    textSize(TEXT_SIZE);
    String s = String.format("%.2f/%.2f @%.1fx", movie.time(), movie.duration(), speed);
    text(s, 0, height - PADDING);
  }
}

/////////////////////////////////////////////////////

class Point {
  int RAD = 15;
  int TEXT_SIZE = 12;
  int PADDING = 4;
  
  int x;
  int y;
  String name;
  
  Point(int x, int y, String name) {
    this.x = x;
    this.y = y;
    this.name = name;
  }
  
  void display() {
    stroke(0);
    line(x - RAD, y, x + RAD, y);
    line(x, y - RAD, x, y + RAD);
    if (name != null) {
      textSize(TEXT_SIZE);
      text(name, x + PADDING, y - PADDING);
    }
  }
}

/////////////////////////////////////////////////////

class Tracker {  
  int POINTS_PER_SECOND = 2;
  
  String objName;
  String path;
  Map<Integer, Point> tracks;
  
  Tracker(String objName) {
    this.objName = objName;
    path = OUTPUT_DIR + objName + ".csv";
    tracks = new HashMap<Integer, Point>();
    loadCsv();
  }
  
  void loadCsv() {
    println("loading csv file...");
    try {
      Table csv = loadTable(path, "header");
      for (TableRow row : csv.rows()) {
        float time = row.getFloat("time");
        int x = row.getInt("x");
        int y = row.getInt("y");
        setPos(time, x, y);
      }
    } catch (NullPointerException ex) {
      println("no file found on load, new csv will be created");
    }
  }
  
  void saveCsv() {
    println("saving csv file...");
    Table csv = new Table();
  
    csv.addColumn("time");
    csv.addColumn("x");
    csv.addColumn("y");
    
    for (Map.Entry entry : tracks.entrySet()) {
        int index = (Integer) entry.getKey();
        Point p = (Point) entry.getValue();
        TableRow row = csv.addRow();
        row.setFloat("time", indexToTime(index));
        row.setInt("x", p.x);
        row.setInt("y", p.y); 
    }
    
    saveTable(csv, path);
  }
  
  void setPos(float time, int x, int y) {
    tracks.put(timeToIndex(time), new Point(x, y, objName));
  }
  
  Point getPos(float time) {
    return tracks.get(timeToIndex(time));
  }
  
  private int timeToIndex(float time) {
    return floor(time * POINTS_PER_SECOND);
  }
  
  private float indexToTime(int index) {
    return ((float) index) / POINTS_PER_SECOND;
  }
}

/////////////////////////////////////////////////////

// performing code on exit
public class DisposeHandler {
   
  DisposeHandler(PApplet pa) {
    pa.registerMethod("dispose", this);
  }
  
  public void dispose() {
    tracker.saveCsv();
    println("bye bye :-)");
  }
}
