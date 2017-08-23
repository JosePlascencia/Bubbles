function Circle(cx, cy, html_id, radius=10)
{
    var html_id = html_id;
    var radius = radius;
    this.info = { cx: cx,  cy: cy };
    
    //private function that generates a random number
    var randomNumberBetween = function(min, max){
        return Math.random()*(max-min) + min;
    }

    this.initialize = function(){
        //give a random velocity for the circle
        this.info.velocity = {
            x: randomNumberBetween(-3,3),
            y: randomNumberBetween(-3,3)
        }

        //create a circle 
        var circle = makeSVG('circle', 
            { 	cx: this.info.cx,
                  cy: this.info.cy,
                  r:  radius,
                  id: html_id,
                  class: 'bubble'
            });

        document.getElementById('svg').appendChild(circle);
    }

    this.update = function(time){
        var el = document.getElementById(html_id);

        //see if the circle is going outside the browser. if it is, reverse the velocity
        if( this.info.cx > document.getElementById("svg").clientWidth - radius)
        {
            this.info.velocity.x = this.info.velocity.x * -1;
            this.info.cx = document.getElementById("svg").clientWidth - radius;
        } 
        else if(this.info.cx < radius)
        {
            this.info.velocity.x = this.info.velocity.x * -1;
            this.info.cx = radius;
        }
        else
        {
            this.info.cx = this.info.cx + this.info.velocity.x*time;
        }
        if( this.info.cy > document.getElementById("svg").clientHeight - radius)
        {
            this.info.velocity.y = this.info.velocity.y * -1;
            this.info.cy = document.getElementById("svg").clientHeight - radius;

        }
        else if (this.info.cy < radius)
        {
            this.info.velocity.y = this.info.velocity.y * -1;
            this.info.cy = radius;
        }
        else
        {
            this.info.cy = this.info.cy + this.info.velocity.y*time;
        }

        el.setAttribute("cx", this.info.cx);
        el.setAttribute("cy", this.info.cy);
    }
    
    this.getID = function()
    {
        return html_id;
    }

    this.getRadius = function()
    {
        return radius;
    }
    
    this.setRadius = function(newRadius)
    {
        if(typeof newRadius == "number")
        {
            radius = newRadius;
        }
    }

    //creates the SVG element and returns it
    var makeSVG = function(tag, attrs) {
        var el= document.createElementNS('http://www.w3.org/2000/svg', tag);
        for (var k in attrs)
        {
            el.setAttribute(k, attrs[k]);
        }
        return el;
    }


    this.initialize();
}

function PlayGround()
{
    var counter = 0;  //counts the number of circles created
    var circles = [ ]; //array that will hold all the circles created in the app
    //a loop that updates the circle's position on the screen
    this.loop = function(){
        for(circle in circles)
        {
            circles[circle].update(1);
            var e1 = document.getElementById(circles[circle].getID());
            var toDelete = false;
            for (c in circles)
            {
                if (circle != c)
                {
                    var e2 = document.getElementById(circles[c].getID());
                    var distancex = circles[circle].info.cx - circles[c].info.cx;
                    var distancey = circles[circle].info.cy - circles[c].info.cy;
                    var distance = Math.sqrt((distancex*distancex) + (distancey*distancey));
                    if(distance < circles[circle].getRadius() + circles[c].getRadius())
                    {
                        e1.setAttribute("r", circles[circle].getRadius() + circles[c].getRadius());
                        circles[circle].setRadius(circles[circle].getRadius() + circles[c].getRadius());
                        e2.parentNode.removeChild(e2);
                        delete circles[c];
                        toDelete = true;
                    }
                }
            }
            if(circles[circle].getRadius() > (document.body.clientWidth/25))
            {
                var rad = circles[circle].getRadius();
                for (var i = 0; i < 20; i ++){
                    var new_circle = new Circle(Math.random()*(document.body.clientWidth-(rad*2) + rad), Math.random()*(document.body.clientHeight-(rad*2) + rad),counter++, rad/20);
                    circles.push(new_circle);
                }
                e1.parentNode.removeChild(e1);
                delete circles[circle];
            }
        }
    }

    this.createNewCircle = function(x,y,t=0){
        var new_circle = new Circle(x,y,counter++, 10+t);
        circles.push(new_circle);
    }
}

var playground = new PlayGround();
setInterval(playground.loop, 15);

var mousedown_time;

function getTime(){
    var date = new Date();
    return date.getTime();
}

document.onmousedown = function(e){
    mousedown_time = getTime();
}

document.onmouseup = function(e){
    time_pressed = getTime() - mousedown_time;
    playground.createNewCircle(e.x,e.y, time_pressed*.05);
}