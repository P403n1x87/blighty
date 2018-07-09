

import os
import textwrap
from math import pi as PI
from threading import Timer

import cairo
import requests
from attrdict import AttrDict
from blighty import CanvasGravity, TextAlign, brush
from blighty.x11 import Canvas, start_event_loop

from fonts import Fonts

try:
    # One of your currently active Wunderground API to perform requests with
    wu_api_key = os.environ["WKEY"]

    # Country of the location forecast are to be requested for
    country    = os.environ["WCOUNTRY"]

    # City/Town the forecast are to be requested for
    city       = os.environ["WCITY"]
except KeyError:
    raise RuntimeError("Environment variables not set.")


ICON_LOOKUP = {
    "chancerain"      : "",
    "nt_chancerain"   : "",
    "partlycloudy"    : "",
    "nt_partlycloudy" : "",
    "clear"           : "",
    "nt_clear"        : "",
    "mostlycloudy"    : "",
    "nt_mostlycloudy" : "",
    "rain"            : "",
    "nt_rain"         : "",
    "cloudy"          : "",
    "snow"            : ""
}  # see http://unitid.nl/iconfonts/?font=weathericons&size=big for more


class DataSource():

    FEATURES = ["conditions", "forecast10day", "astronomy", "hourly", "satellite"]

    def __init__(self):
        self.data = None

    def generate_wu_url(self):
        return 'http://api.wunderground.com/api/{key}/{features}/q/{country}/{city}.json'.format(
            key = wu_api_key,
            features = "/".join(DataSource.FEATURES),
            country = country.replace(" ", "%20"),
            city = city.replace(" ", "%20")
        )

    def download_data(self):
        try:
            r = requests.get(self.generate_wu_url())

        except requests.exceptions.ConnectionError:
            print("Connection error. Retrying in 5 seconds")
            self.timer = Timer(5.0, self.download_data)

        else:
            if r.status_code != 200:
                raise RuntimeError("Wunderground request failed: {}".format(r.status_code))

            self.data = AttrDict(r.json())
            self.timer = Timer(60.0 * 15, self.download_data)

        self.timer.start()

    def get_data(self):
        return self.data

    def start(self):
        self.download_data()

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None


class Wunderground(Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wrapper = textwrap.TextWrapper(width=50)
        self.datasource = None

    @staticmethod
    def build(x = 0, y = 64, gravity = CanvasGravity.NORTH):
        return Wunderground(
            x = x,
            y = y,
            width = 480,
            height = 400,
            gravity = gravity,
            interval = 10000
        )

    def set_datasource(self, datasource):
        self.datasource = datasource

    def show(self):
        super().show()

        self.datasource.start()

    def on_button_pressed(self, button, state, x, y):
        if button == 1:
            self.datasource.stop()
            self.dispose()

    def draw_location(ctx, data):
        ctx.save()

        X = 130

        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_font_size(32)
        ex = ctx.write_text(ctx.canvas.width - 4, 0, data.city, align = TextAlign.BOTTOM_RIGHT)
        ctx.set_font_size(18)
        ex = ctx.write_text(ctx.canvas.width - 4, 4 + ex.height, data.state_name, align = TextAlign.BOTTOM_RIGHT)

        ctx.set_font_size(14)
        ctx.write_text(X + 60, 26, "{:.2f}".format(float(data.latitude)), align = TextAlign.TOP_RIGHT)
        ctx.write_text(X + 60, 48, "{:.2f}".format(float(data.longitude)), align = TextAlign.TOP_RIGHT)
        ctx.select_font_face(*Fonts.LAKSAMAN_BOLD)
        ctx.write_text(X, 26, "LA", align = TextAlign.TOP_LEFT)
        ctx.write_text(X, 48, "LO", align = TextAlign.TOP_LEFT)

        ctx.restore()

    def draw_astronomy(ctx, data):
        ctx.save()

        X = 0
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_font_size(14)
        ctx.write_text(X + 60, 26, "{hour}:{minute}".format(**data.sunrise), align = TextAlign.TOP_RIGHT)
        ctx.write_text(X + 60, 48, "{hour}:{minute}".format(**data.sunset), align = TextAlign.TOP_RIGHT)
        ctx.write_text(X + 120, 26, "{hour}:{minute}".format(**data.moonrise), align = TextAlign.TOP_RIGHT)
        ctx.write_text(X + 120, 48, "{hour}:{minute}".format(**data.moonset), align = TextAlign.TOP_RIGHT)

        ctx.select_font_face(*Fonts.WEATHER_ICON_NORMAL)
        ctx.set_font_size(16)
        ctx.write_text(X, 26, "", align = TextAlign.TOP_LEFT)
        ctx.write_text(X, 48, "", align = TextAlign.TOP_LEFT)
        ctx.write_text(X + 70, 26, "", align = TextAlign.TOP_LEFT)
        ctx.write_text(X + 70, 48, "", align = TextAlign.TOP_LEFT)

        ctx.restore()

    def draw_current_condition(ctx, data):
        X, Y = 68, 170
        ctx.save()
        ctx.set_source_rgba(1, 1, 1, .2)
        ctx.arc(X, Y - 36, 60, 0, 2 * PI)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 1)

        ctx.set_font_size(14)
        ctx.write_text(X, 210, data.weather, align = TextAlign.TOP_MIDDLE)

        ctx.set_font_size(64)
        ctx.write_text(X + 70, 134, str(data.temp_c) + "˚C")

        ctx.set_font_size(14)
        ctx.write_text(ctx.canvas.width - 4, 96, data.relative_humidity, align = TextAlign.TOP_RIGHT)
        ctx.write_text(ctx.canvas.width - 4, 116, "{:.1f} m/s".format(data.wind_kph * 5 / 18), align = TextAlign.TOP_RIGHT)
        ctx.write_text(ctx.canvas.width - 4, 136, "{} mb".format(data.pressure_mb), align = TextAlign.TOP_RIGHT)

        ctx.set_font_size(12)
        ctx.write_text(ctx.canvas.width - 8, ctx.canvas.height, data.observation_time, align = TextAlign.TOP_RIGHT)

        ctx.select_font_face(*Fonts.WEATHER_ICON_NORMAL)
        ctx.set_font_size(16)
        ctx.write_text(ctx.canvas.width - 100, 96, "", align = TextAlign.TOP_LEFT)
        ctx.write_text(ctx.canvas.width - 100, 116, "", align = TextAlign.TOP_LEFT)
        ctx.write_text(ctx.canvas.width - 100, 136, "", align = TextAlign.TOP_LEFT)
        ctx.set_font_size(80)
        ctx.write_text(X, Y, ICON_LOOKUP[data.icon], align = TextAlign.TOP_MIDDLE)

        ctx.restore()

    @brush
    def write_forecast(ctx, data):
        ctx.save()

        ctx.set_font_size(13)
        ctx.set_source_rgba(1, 1, 1, 1)
        X, Y = 138, 156
        for line in ctx.canvas.wrapper.wrap(text=data.txt_forecast.forecastday[0].fcttext_metric):
            ex = ctx.write_text(X, Y, line, align = TextAlign.TOP_LEFT)
            Y += max(18, ex.height * 1.25)

        ctx.restore()

    def draw_hourly(ctx, data):
        X, Y = 160, 210
        WW = ctx.canvas.width - (X + 20)
        H = 64
        N = 6
        W = int(WW / N)

        def draw_hour(x, y, hour, icon, temp):
            ctx.set_font_size(14)
            ctx.write_text(x + (W >> 1), y + 10, hour, align = TextAlign.TOP_MIDDLE)
            ctx.set_font_size(11)
            ex = ctx.write_text(x + W - 8, y + H, temp + "˚C", align = TextAlign.TOP_RIGHT)
            ctx.save()
            ctx.select_font_face(*Fonts.WEATHER_ICON_NORMAL)
            ctx.write_text(x + 8, y + H, "", align = TextAlign.TOP_LEFT)
            ctx.set_font_size(28)
            ctx.write_text(x + (W >> 1), y + H - ex.height * 2, icon, align = TextAlign.TOP_MIDDLE)
            ctx.restore()

        ctx.save()
        ctx.set_source_rgba(1, 1, 1, .8)
        ctx.set_font_size(14)

        pop_data = []
        for i in range(min(len(data), N + 1)):
            pop_data.append(float(data[i]['pop']))

        ctx.set_source_rgba(.8, .8, .8, .8)
        ctx.set_line_width(.5)
        for i in range(3):
            ctx.move_to(X + 20, Y + 14 + 36 * i / 2)
            ctx.line_to(X + 20 + WW, Y + 14 + 36 * i / 2)
            ctx.stroke()
        ctx.set_line_width(2)
        ctx.set_source_rgba(1, 1, 1, .75)
        ctx.move_to(X + 20, Y + 14 + 36 * (1 - pop_data[0]/100))
        for i in range(1, len(pop_data)):
            ctx.line_to(X + 20 + i * W, Y + 14 + 36 * (1 - pop_data[i]/100))
        ctx.stroke_preserve()
        ctx.line_to(X + 20 + (N + 1) * W, Y + 14 + 36)
        ctx.line_to(X + 20, Y + 14 + 36)
        ctx.line_to(X + 20, Y + 14 + 36 * (1 - pop_data[0]/100))

        bg = cairo.LinearGradient(X, Y + 14, X, Y + 50)
        bg.add_color_stop_rgba(0, 1, 1, 1, .5)
        bg.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(bg)
        ctx.fill()

        ctx.set_source_rgba(1, 1, 1, 1)
        for i in range(min(len(data), N)):
            draw_hour(X + 20 + i * W, Y , "{}:{}".format(data[i].FCTTIME.hour, data[i].FCTTIME.min), ICON_LOOKUP[data[i].icon], data[i].temp.metric)

        ctx.translate(X, Y + (H >> 1))
        ctx.rotate(-PI / 2)
        ctx.set_font_size(14)
        ctx.write_text(0, -2, "LATER", align = TextAlign.TOP_MIDDLE)
        ctx.write_text(0, 2, "TODAY", align = TextAlign.BOTTOM_MIDDLE)

        ctx.restore()

    def draw_days(ctx, data):
        X, Y = 160, 300
        WW = ctx.canvas.width - (X + 20)
        H = 80
        N = min(4, len(data))
        W = int(WW / N)

        def draw_day(x, y, day, icon, temp):
            ctx.set_font_size(14)
            ctx.write_text(x + (W >> 1), y + 10, day, align = TextAlign.TOP_MIDDLE)
            ctx.set_font_size(28)
            ex = ctx.write_text(x + 8, y + H, temp['max'], align = TextAlign.TOP_LEFT)
            icon_h = int(ex.height)
            ctx.set_font_size(14)
            ctx.write_text(x + 16 + ex.width, y + H - (icon_h >> 1), "˚C", align = TextAlign.TOP_LEFT)
            ctx.write_text(x + 16 + ex.width, y + H, temp['min'], align = TextAlign.TOP_LEFT)
            ctx.save()
            ctx.select_font_face(*Fonts.WEATHER_ICON_NORMAL)
            ctx.set_font_size(28)
            ctx.write_text(x + (W >> 1), y + H - icon_h * 1.5, icon, align = TextAlign.TOP_MIDDLE)
            ctx.restore()

        ctx.save()
        ctx.set_source_rgba(1, 1, 1, .8)
        ctx.set_font_size(14)

        for i in range(N):
            temp = {'max' : data[i].high.celsius, 'min' : data[i].low.celsius}
            draw_day(X + 20 + i * W, Y, data[i].date.weekday_short.upper(), ICON_LOOKUP[data[i].icon], temp)

        ctx.translate(X, Y + (H >> 1))
        ctx.rotate(-PI / 2)
        ctx.set_font_size(14)
        ctx.write_text(0, -2, "NEXT", align = TextAlign.TOP_MIDDLE)
        ctx.write_text(0, 2, "DAYS", align = TextAlign.BOTTOM_MIDDLE)

        ctx.restore()

    def draw_moon(ctx, moon):
        X, Y = 68, 290
        R = 40
        p = int(moon.percentIlluminated)

        ctx.save()

        ctx.translate(X, Y)

        ctx.set_source_rgb(1, 1, 1)
        ctx.set_font_size(14)
        ctx.write_text(0, R + 24, moon.phaseofMoon, CanvasGravity.NORTH)
        ctx.write_text(0, R + 42, "{} days -- {}%".format(moon.ageOfMoon, moon.percentIlluminated), CanvasGravity.NORTH)

        if int(moon.ageOfMoon) < 14:
            ctx.rotate(PI)

        ctx.arc(0, 0, R, PI/2, -PI/2)
        ctx.fill()
        ctx.scale(abs(1 - 2 * p / 100), 1)
        ctx.arc(0, 0, R, 0, 2 * PI)
        if p < 50:
            ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.fill()

        ctx.restore()

    @brush
    def print_msg(ctx, msg):
        ctx.save()
        ctx.set_font_size(24)
        ctx.set_source_rgb(1, 1, 1)
        ctx.write_text(ctx.canvas.width >> 1, ctx.canvas.height >> 1, msg, align = TextAlign.CENTER_MIDDLE)
        ctx.restore()

    def on_draw(self, ctx):
        print("Drawing")
        ctx.select_font_face(*Fonts.LAKSAMAN_NORMAL)

        if self.datasource is None:
            self.interval = 10000
            ctx.print_msg("No data")
            return

        data = self.datasource.get_data()
        if data is None:
            self.interval = 10000
            ctx.print_msg("No data")
            return

        self.interval = 60000

        ctx.draw_location(data.current_observation.display_location)
        ctx.draw_astronomy(data.moon_phase)
        ctx.draw_current_condition(data.current_observation)
        ctx.write_forecast(data.forecast)
        if len(data.hourly_forecast) > 0:
            ctx.draw_hourly(data.hourly_forecast)
        ctx.draw_days(data.forecast.simpleforecast.forecastday[1:])
        ctx.draw_moon(data.moon_phase)


###############################################################################


if __name__ == "__main__":
    w = Wunderground.build()

    w.set_datasource(DataSource())
    w.show()

    start_event_loop()
