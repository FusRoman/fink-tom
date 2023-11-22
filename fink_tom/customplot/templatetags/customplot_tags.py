from plotly import offline
import plotly.graph_objs as go
import plotly.express as px
from django import template
import pandas as pd
import numpy as np
from astropy.time import Time
import astropy.units as u
from tom_targets.forms import TargetVisibilityForm
from datetime import datetime, timedelta
from astroplan import Observer, FixedTarget, is_observable, observability_table, is_event_observable
from astroplan.utils import time_grid_from_range
from astropy.coordinates import SkyCoord

from fink_tom.start_cadence_hooks import is_target_observable, gvom_network

from tom_targets.models import Target


register = template.Library()

def return_time_constraints(
    observatory: Observer,
    target: Target,
    constraints: list,
    start: float,
    end: float,
    time_resolution: float,
):
    time_range = Time([start, end], format="datetime")
    target = FixedTarget(coord=SkyCoord(ra=target.ra * u.deg, dec=target.dec * u.deg), name=target.name)
    observable = is_observable(constraints, observatory, target, time_range=time_range)
    if observable:
        obs_table = observability_table(
            constraints, observatory, [target], time_range=time_range
        )
        time_grid = time_grid_from_range(
            [time_range[0], time_range[1]], time_resolution=time_resolution
        )

        test_observability = is_event_observable(
            constraints,
            observatory,
            target,
            time_grid
        )[0]

        # observability_grid = np.zeros((len(constraints), len(time_grid)))

        # for i, constraint in enumerate(constraints):
        #     # Evaluate each constraint
        #     observability_grid[i, :] = constraint(observatory, target, times=time_grid)

        # all_cons_true = np.array(observability_grid).all(axis=0)
        return (
            time_grid[test_observability],
            obs_table["fraction of time observable"].value[0],
        )
    else:
        return np.array([]), 0.0

def gvom_target_observability(target, start, end):
    obs_res = [
        [
            obs.name,
            *return_time_constraints(
                obs.observatory,
                target,
                obs.constraints,
                start,
                end,
                10 * u.minute,
            ),
        ]
        for obs in gvom_network
    ]
    return np.array(obs_res, dtype="object")

def is_target_observable(target, start, end):
    observability = gvom_target_observability(target, start, end)

    res_pdf = pd.DataFrame(
        observability, columns=["observatory", "observable_time", "observable_fraction"]
    )
    res_pdf["objectId"] = target.name
    return res_pdf


from tom_observations.utils import get_sidereal_visibility
@register.inclusion_tag("customplot/gvom_observability.html", takes_context=True)
def gvom_observability(context, fast_render=False, width=600, height=400, background=None, label_color=None, grid=True):

    request = context['request']
    plan_form = TargetVisibilityForm()
    observability_graph = ''
    if all(request.GET.get(x) for x in ['start_time', 'end_time']) or fast_render:
        plan_form = TargetVisibilityForm({
            'start_time': request.GET.get('start_time', datetime.utcnow()),
            'end_time': request.GET.get('end_time', datetime.utcnow() + timedelta(days=1)),
            'airmass': request.GET.get('airmass', 2.5),
            'target': context['object']
        })
        if plan_form.is_valid():
            start_time = plan_form.cleaned_data['start_time']
            end_time = plan_form.cleaned_data['end_time']

            pdf_obs = is_target_observable(context['object'], start_time, end_time)
            t = pd.concat(
                [
                    pd.DataFrame(
                        [
                            dict(
                                Observatory=obs.name,
                                Start=Time(time, format="jd").iso,
                                Finish=(Time(time, format="jd") + (10 * u.minute)).iso,
                            )
                            for time in pdf_obs[pdf_obs["observatory"] == obs.name][
                                "observable_time"
                            ].values[0]
                        ]
                    )
                    for obs in gvom_network
                ]
            )
            fig = px.timeline(
                t,
                x_start="Start",
                x_end="Finish",
                y="Observatory",
                color="Observatory",
                title=f"{context['object'].name} Observability by gvom network",
            )

            layout = go.Layout(
                fig.layout
            )
            layout.legend.font.color = label_color
            fig = go.Figure(data=fig.data, layout=layout)
            fig.update_yaxes(showgrid=grid, color=label_color, showline=True, linecolor=label_color, mirror=True)
            fig.update_xaxes(showgrid=grid, color=label_color, showline=True, linecolor=label_color, mirror=True)
            observability_graph = offline.plot(
                fig, output_type='div', show_link=False
            )
    # Add plot to the template context
    return {'observability_graph': observability_graph}


    # request = context['request']
    # plan_form = TargetVisibilityForm()
    # observability_graph = ''

    # if all(request.GET.get(x) for x in ['start_time', 'end_time']) or fast_render:
    #     plan_form = TargetVisibilityForm({
    #             'start_time': request.GET.get('start_time', datetime.utcnow()),
    #             'end_time': request.GET.get('end_time', datetime.utcnow() + timedelta(days=1)),
    #             'airmass': request.GET.get('airmass', 2.5),
    #             'target': context['object']
    #         })
        
    #     if plan_form.is_valid():

    #         start_time = plan_form.cleaned_data['start_time']
    #         end_time = plan_form.cleaned_data['end_time']
    #         target = plan_form.cleaned_data['target']

            # pdf_obs = is_target_observable(target, start_time, end_time)


    layout = go.Layout(
        yaxis=dict(autorange="reversed"),
        width=600,
        height=400,
        paper_bgcolor=None,
        plot_bgcolor=None,
    )

    # t = pd.concat(
    #     [
    #         pd.DataFrame(
    #             [
    #                 dict(
    #                     Observatory=obs.name,
    #                     Start=Time(time, format="jd").iso,
    #                     Finish=(Time(time, format="jd") + (10 * u.minute)).iso,
    #                 )
    #                 for time in pdf_obs[pdf_obs["observatory"] == obs.name][
    #                     "observable_time"
    #                 ].values[0]
    #             ]
    #         )
    #         for obs in gvom_network
    #     ]
    # )

    # fig = px.timeline(
    #     t,
    #     x_start="Start",
    #     x_end="Finish",
    #     y="Observatory",
    #     color="Observatory",
    #     title=f"{target.name} Observability by gvom network",
    # )
    plot_data = [
        go.Scatter(
            x=[0, 1], y=[0, 1]
        )
    ]

    fig = go.Figure(data=plot_data, layout=layout)
    fig.update_yaxes(showgrid=True, color=None, showline=True, linecolor=None, mirror=True)
    fig.update_xaxes(showgrid=True, color=None, showline=True, linecolor=None, mirror=True)

    observability_graph = offline.plot(
                fig, output_type='div', show_link=False
            )

    print(observability_graph)

    return {
        'observability_graph': observability_graph
    }

