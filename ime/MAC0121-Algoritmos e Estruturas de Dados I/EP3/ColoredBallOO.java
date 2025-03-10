import java.awt.Color;

public class ColoredBallOO {
    private Vector position;
    private Vector velocity;
    private final double radius;
    private final Color color;

    public ColoredBallOO(Vector p, Vector v, double r, Color c) {
        position = p;
        velocity = v;
        radius = r;
        color = c;
    }

    public Vector pos() {
        return position;
    }

    public Vector vel() {
        return velocity;
    }

    public double radius() {
        return radius;
    }

    public void setVel(Vector v) {
        velocity = v;
    }

    public void updatePosition(double dt) {
        // p = p + dt*v
        position = position.plus(velocity.scale(dt));
    }

    public void treatWalls(double size, double dt) {
        Vector nextPos = position.plus(velocity.scale(dt));
        if (nextPos.cartesian(0) - radius < 0 || nextPos.cartesian(0) + radius > size) {
            // vx = -vx se bateu na parede na esquerda ou direita
            double[] v = {-velocity.cartesian(0), velocity.cartesian(1)};
            velocity = new Vector(v);
        }
        if (nextPos.cartesian(1) - radius < 0 || nextPos.cartesian(1) + radius > size) {
            // vy = -vy se bateu na parede de cima ou de baixo
            double[] v = {velocity.cartesian(0), -velocity.cartesian(1)};
            velocity = new Vector(v);
        }
    }

    public void move(double size, double dt) {
        treatWalls(size, dt);
        updatePosition(dt);
    }

    public void draw() {
        StdDraw.setPenColor(color);
        StdDraw.filledCircle(position.cartesian(0), position.cartesian(1), radius);
    }
}