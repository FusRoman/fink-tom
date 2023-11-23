from plotly import offline
import plotly.graph_objs as go
from django import template
from tom_targets.forms import TargetVisibilityForm
from datetime import datetime, timedelta

from fink_tom.observability import observability_figure

register = template.Library()

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

            fig = observability_figure(context['object'], start_time, end_time)

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

