"""
PDF Report Generation Service.

Generates professional PDF reports for insolvency analysis and layoff simulations
using ReportLab.
"""

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER


class PDFReportGenerator:
    """Generate professional PDF reports for financial analysis."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d'),
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4a5568'),
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2d3748'),
            borderPadding=5,
        ))

        # Metric label style
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#718096'),
        ))

        # Metric value style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
        ))

        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceBefore=5,
            spaceAfter=5,
            bulletIndent=10,
        ))

    def _get_risk_color(self, risk_category: str) -> colors.Color:
        """Get color based on risk category."""
        color_map = {
            "Low": colors.HexColor('#38a169'),      # Green
            "Medium": colors.HexColor('#d69e2e'),   # Yellow/Orange
            "High": colors.HexColor('#e53e3e'),     # Red
            "Safe": colors.HexColor('#38a169'),     # Green
            "Grey": colors.HexColor('#d69e2e'),     # Yellow
            "Distress": colors.HexColor('#e53e3e'), # Red
        }
        return color_map.get(risk_category, colors.black)

    def _create_header(self, title: str, subtitle: str = None) -> list:
        """Create report header elements."""
        elements = []

        # Title
        elements.append(Paragraph(title, self.styles['ReportTitle']))

        # Subtitle
        if subtitle:
            elements.append(Paragraph(subtitle, self.styles['ReportSubtitle']))

        # Date
        date_str = datetime.now().strftime("%B %d, %Y at %H:%M")
        elements.append(Paragraph(
            f"Generated: {date_str}",
            self.styles['ReportSubtitle']
        ))

        # Horizontal line
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#e2e8f0'),
            spaceBefore=5,
            spaceAfter=20,
        ))

        return elements

    def _create_metric_box(self, label: str, value: str, color: colors.Color = None) -> Table:
        """Create a styled metric display box."""
        if color:
            value_style = ParagraphStyle(
                'MetricValueColored',
                parent=self.styles['MetricValue'],
                textColor=color,
            )
        else:
            value_style = self.styles['MetricValue']

        data = [
            [Paragraph(label, self.styles['MetricLabel'])],
            [Paragraph(str(value), value_style)],
        ]

        table = Table(data, colWidths=[2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def generate_insolvency_report(
        self,
        company_id: str,
        company_name: str,
        prediction: dict[str, Any],
        explanation: dict[str, Any],
    ) -> bytes:
        """
        Generate an insolvency analysis PDF report.

        Args:
            company_id: Company identifier
            company_name: Company name
            prediction: Prediction results (probability, risk_category, z_score, etc.)
            explanation: SHAP explanation (top_risk_drivers, shap_values)

        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        elements = []

        # Header
        elements.extend(self._create_header(
            "Insolvency Risk Assessment Report",
            f"{company_name} ({company_id})" if company_name else company_id
        ))

        # Executive Summary Section
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        # Risk metrics in a row
        risk_category = prediction.get('risk_category', 'Unknown')
        probability = prediction.get('probability_of_distress', 0)
        z_score = prediction.get('z_score', 0)
        z_zone = prediction.get('z_score_zone', 'Unknown')
        time_to_event = prediction.get('estimated_time_to_event')

        metrics_data = [
            [
                self._create_metric_box(
                    "Risk Category",
                    risk_category,
                    self._get_risk_color(risk_category)
                ),
                self._create_metric_box(
                    "Probability of Distress",
                    f"{probability:.1%}",
                    self._get_risk_color(risk_category)
                ),
                self._create_metric_box(
                    "Altman Z-Score",
                    f"{z_score:.2f} ({z_zone})",
                    self._get_risk_color(z_zone)
                ),
            ]
        ]

        metrics_table = Table(metrics_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))

        # Time to Event (if applicable)
        if time_to_event:
            elements.append(Paragraph(
                f"<b>Estimated Time to Financial Distress:</b> {time_to_event} years",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 20))

        # Risk Drivers Section
        elements.append(Paragraph("Top Risk Drivers", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "The following factors contribute most significantly to the risk assessment, "
            "based on SHAP (SHapley Additive exPlanations) analysis:",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 10))

        # Risk drivers table
        top_drivers = explanation.get('top_risk_drivers', [])[:10]
        if top_drivers:
            driver_data = [['Rank', 'Risk Factor', 'Value', 'Impact', 'Direction']]

            for i, driver in enumerate(top_drivers, 1):
                feature = driver.get('feature', '').replace('_', ' ').title()
                value = driver.get('feature_value', 0)
                shap_value = driver.get('shap_value', 0)

                # Format value
                if isinstance(value, float):
                    value_str = f"{value:.4f}"
                else:
                    value_str = str(value)

                # Determine direction indicator
                if shap_value > 0:
                    direction = "↑ Increases Risk"
                else:
                    direction = "↓ Decreases Risk"

                driver_data.append([
                    str(i),
                    feature,
                    value_str,
                    f"{shap_value:+.4f}",
                    direction,
                ])

            driver_table = Table(
                driver_data,
                colWidths=[0.5*inch, 2.2*inch, 1*inch, 1*inch, 1.5*inch]
            )
            driver_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ]))
            elements.append(driver_table)
        elements.append(Spacer(1, 20))

        # Recommendations Section
        elements.append(Paragraph("Recommendations", self.styles['SectionHeader']))

        recommendations = self._generate_insolvency_recommendations(
            risk_category, probability, z_score, top_drivers
        )

        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['Recommendation']))

        elements.append(Spacer(1, 20))

        # Disclaimer
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#e2e8f0'),
            spaceBefore=20,
            spaceAfter=10,
        ))
        elements.append(Paragraph(
            "<i>Disclaimer: This report is generated by an automated system using machine learning "
            "models. The predictions and recommendations should be used as one input among many "
            "in financial decision-making. Always consult with qualified financial professionals "
            "before making significant business decisions.</i>",
            ParagraphStyle('Disclaimer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey)
        ))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_insolvency_recommendations(
        self,
        risk_category: str,
        probability: float,
        z_score: float,
        top_drivers: list
    ) -> list[str]:
        """Generate contextual recommendations based on analysis."""
        recommendations = []

        if risk_category == "High":
            recommendations.append(
                "URGENT: Immediate financial restructuring is recommended. Consider engaging "
                "a turnaround specialist or financial advisor."
            )
            recommendations.append(
                "Review and renegotiate existing debt obligations to improve cash flow."
            )
            recommendations.append(
                "Implement cost reduction measures across all departments."
            )
        elif risk_category == "Medium":
            recommendations.append(
                "Monitor financial ratios closely on a monthly basis."
            )
            recommendations.append(
                "Develop a contingency plan for potential financial stress scenarios."
            )
            recommendations.append(
                "Consider diversifying revenue streams to reduce risk."
            )
        else:
            recommendations.append(
                "Continue current financial management practices."
            )
            recommendations.append(
                "Consider strategic investments for growth opportunities."
            )

        # Add recommendations based on top risk drivers
        for driver in top_drivers[:3]:
            feature = driver.get('feature', '')
            if 'debt' in feature.lower() and driver.get('shap_value', 0) > 0:
                recommendations.append(
                    "Focus on debt reduction strategies to improve leverage ratios."
                )
            if 'working_capital' in feature.lower() and driver.get('shap_value', 0) > 0:
                recommendations.append(
                    "Improve working capital management through better inventory and receivables management."
                )
            if 'profit' in feature.lower() and driver.get('shap_value', 0) > 0:
                recommendations.append(
                    "Review pricing strategies and operational efficiency to improve profit margins."
                )

        return recommendations[:6]  # Limit to 6 recommendations

    def generate_layoff_report(
        self,
        simulation_params: dict[str, Any],
        summary: dict[str, Any],
        recommendations: list[dict[str, Any]],
        department_breakdown: dict[str, int],
    ) -> bytes:
        """
        Generate a layoff simulation PDF report.

        Args:
            simulation_params: Parameters used for simulation (budget_cut_percent, min_per_dept)
            summary: Summary statistics (target savings, actual savings, etc.)
            recommendations: List of layoff recommendations
            department_breakdown: Count of layoffs per department

        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        elements = []

        # Header
        elements.extend(self._create_header(
            "Workforce Optimization Report",
            "Layoff Simulation Analysis"
        ))

        # Simulation Parameters Section
        elements.append(Paragraph("Simulation Parameters", self.styles['SectionHeader']))

        params_data = [
            ['Parameter', 'Value'],
            ['Target Budget Cut', f"{simulation_params.get('budget_cut_percent', 0):.1f}%"],
            ['Minimum Employees per Department', str(simulation_params.get('min_per_dept', 1))],
        ]

        params_table = Table(params_data, colWidths=[3*inch, 2*inch])
        params_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(params_table)
        elements.append(Spacer(1, 20))

        # Summary Statistics Section
        elements.append(Paragraph("Cost Savings Analysis", self.styles['SectionHeader']))

        target_savings = summary.get('target_monthly_savings', 0)
        actual_savings = summary.get('actual_monthly_savings', 0)
        employees_affected = summary.get('employees_affected', 0)
        savings_percent = summary.get('savings_achieved_percent', 0)

        # Savings metrics
        savings_data = [
            [
                self._create_metric_box("Target Monthly Savings", f"${target_savings:,.0f}"),
                self._create_metric_box("Actual Monthly Savings", f"${actual_savings:,.0f}"),
                self._create_metric_box("Savings Achieved", f"{savings_percent:.1f}%"),
            ],
            [
                self._create_metric_box("Employees Affected", str(employees_affected)),
                self._create_metric_box("Annual Savings", f"${actual_savings * 12:,.0f}"),
                self._create_metric_box(
                    "Target Met",
                    "Yes" if actual_savings >= target_savings else "No",
                    colors.HexColor('#38a169') if actual_savings >= target_savings else colors.HexColor('#e53e3e')
                ),
            ],
        ]

        savings_table = Table(savings_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
        savings_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(savings_table)
        elements.append(Spacer(1, 20))

        # Department Impact Analysis
        elements.append(Paragraph("Department Impact Analysis", self.styles['SectionHeader']))

        if department_breakdown:
            dept_data = [['Department', 'Employees Affected', 'Impact Level']]

            for dept, count in sorted(department_breakdown.items(), key=lambda x: x[1], reverse=True):
                if count >= 5:
                    impact = "High"
                elif count >= 3:
                    impact = "Medium"
                else:
                    impact = "Low"
                dept_data.append([dept, str(count), impact])

            dept_table = Table(dept_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            dept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ]))
            elements.append(dept_table)
        else:
            elements.append(Paragraph("No department breakdown available.", self.styles['Normal']))

        elements.append(Spacer(1, 20))

        # Layoff Recommendations List
        elements.append(Paragraph("Detailed Layoff Recommendations", self.styles['SectionHeader']))

        # Filter to only recommended layoffs
        layoff_list = [r for r in recommendations if r.get('layoff_recommended', False)]

        if layoff_list:
            # Show first 30 recommendations
            display_list = layoff_list[:30]

            rec_data = [['#', 'Employee', 'Department', 'Monthly Income', 'Retention Score', 'Reason']]

            for i, rec in enumerate(display_list, 1):
                rec_data.append([
                    str(i),
                    rec.get('name', 'N/A'),
                    rec.get('department', 'N/A'),
                    f"${rec.get('monthly_income', 0):,}",
                    f"{rec.get('retention_score', 0):.1f}",
                    rec.get('layoff_reason', 'N/A')[:30] + "..." if len(rec.get('layoff_reason', '')) > 30 else rec.get('layoff_reason', 'N/A'),
                ])

            rec_table = Table(
                rec_data,
                colWidths=[0.4*inch, 1.3*inch, 1.2*inch, 1*inch, 0.9*inch, 1.6*inch]
            )
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ]))
            elements.append(rec_table)

            if len(layoff_list) > 30:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(
                    f"<i>Showing 30 of {len(layoff_list)} total recommendations.</i>",
                    self.styles['Normal']
                ))
        else:
            elements.append(Paragraph("No layoff recommendations generated.", self.styles['Normal']))

        elements.append(Spacer(1, 20))

        # Implementation Guidelines
        elements.append(Paragraph("Implementation Guidelines", self.styles['SectionHeader']))

        guidelines = [
            "Review all recommendations with HR and legal teams before implementation.",
            "Ensure compliance with local labor laws and contractual obligations.",
            "Develop a communication plan for affected employees.",
            "Prepare severance packages in accordance with company policy.",
            "Plan for knowledge transfer from departing employees.",
            "Consider offering voluntary separation packages before involuntary layoffs.",
            "Document all decisions and reasoning for compliance purposes.",
        ]

        for guideline in guidelines:
            elements.append(Paragraph(f"• {guideline}", self.styles['Recommendation']))

        # Disclaimer
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#e2e8f0'),
            spaceBefore=10,
            spaceAfter=10,
        ))
        elements.append(Paragraph(
            "<i>Disclaimer: This report is generated by an automated system using machine learning "
            "models. These recommendations should be reviewed by HR professionals and legal counsel "
            "before any action is taken. The system does not account for individual circumstances, "
            "legal requirements, or contractual obligations.</i>",
            ParagraphStyle('Disclaimer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey)
        ))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
